#!/usr/bin/env python
"""Main Plexorcist execution file!"""

__version__ = "1.3.3"

import os
import argparse
import configparser
import functools
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import urllib.parse
import requests
import xmltodict

# Get the absolute path of the directory containing the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path of the INI file
config_file_path = os.path.join(script_dir, "plexorcist.ini")

# Read the config file
config = configparser.ConfigParser()
config.read(config_file_path)

# Set the script properties
PLEX_HOSTNAME = config.get("plex", "hostname")
PLEX_PORT = config.get("plex", "port")
PLEX_BASE = f"http://{PLEX_HOSTNAME}:{PLEX_PORT}"
PLEX_TOKEN = config.get("plex", "token")
PLEX_LIBRARIES = [
    library.strip() for library in config.get("plex", "libraries").split(",")
]
IFTTT_WEBHOOK = config.get("plex", "ifttt_webhook")
WHITELIST = [video.strip() for video in config.get("plex", "whitelist").split(",")]

# Set the translations
I18N = {}
for translation in config.options("i18n"):
    I18N[translation] = config.get("i18n", translation)

# Set the log file name
LOG_FILE = os.path.join(script_dir, "plexorcist.log")

# Create a rotating file handler with a maximum size of 1 MB
handler = RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=2)
# Configure the logger with the rotating file handler
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[handler],
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Define command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--config", action="store_true", help="update config file")
parser.add_argument(
    "--version", action="store_true", help="prints the current installed version"
)

# Parse command-line arguments
input_args = parser.parse_args()


def update_config_file():
    """Update the config file via user prompt"""

    print(
        "Behold, if thou appendeth the flag 'config' unto thy command,\n"
        + "thou shalt be granted the power to update thy configuration file with new values!\n\n"
    )

    new_config_values = {}

    # Prompt the user for new values for each option in the "plex" section
    for item in config.options("plex"):
        value_prompt = input(f"Enter the new {item} (or press enter to skip): ")
        if value_prompt:
            new_config_values[item] = value_prompt

    # Update the values in the config object
    for option, value in new_config_values.items():
        config.set("plex", option, value)

    print(
        "\n\nVerily, I thanketh thee for thine input, forsooth, and may thy configuration file\n"
        + "be blessed with new values that shall bring forth great fruit in thine endeavours!"
    )

    # Write the changes back to the INI file
    with open(config_file_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)
        logging.info("Config file has been updated with new values!")


def plexorcise():
    """Main plexorcise method"""

    # Fetch the Plex data
    for library in PLEX_LIBRARIES:
        response = make_request(
            url=f"{PLEX_BASE}/library/sections/{library}/allLeaves",
            headers={"X-Plex-Token": PLEX_TOKEN},
        )

        # Handle videos
        handle_videos(response=response)


def handle_videos(response):
    """Handle videos"""

    if response is not None:
        data = xmltodict.parse(response.content)
        videos = data["MediaContainer"]["Video"]
        media_type = data["MediaContainer"]["@viewGroup"]
        older_than = handle_older_than()

        if videos and len(videos) > 0:
            # Filter watched videos
            watched_videos = filter_videos(videos=videos, older_than=older_than)

            # Delete watched videos and send notification
            delete_videos(watched_videos=watched_videos, media_type=media_type)


def handle_older_than():
    """Handle older than time diff"""

    older_than_string = config.get("plex", "older_than").split()
    older_than_dict = {"days": 0, "hours": 0, "minutes": 0}
    time_units = {"d": "days", "h": "hours", "m": "minutes"}

    for time in older_than_string:
        unit = time[-1]
        value = int(time[:-1])
        if unit in time_units:
            older_than_dict[time_units[unit]] = value

    older_than_timedelta = timedelta(**older_than_dict)
    time_ago = datetime.now() - older_than_timedelta
    unixtime = int(time_ago.timestamp())

    return unixtime if older_than_string[0] != "0" else 0


def filter_videos(videos, older_than):
    """Filter videos"""

    # Check if video was watched and / or is older than
    def is_watched_video(video):
        return (
            video.get("@viewCount")
            and int(video["@viewCount"]) >= 1
            and (
                older_than == 0
                or (
                    video.get("@lastViewedAt")
                    and int(video["@lastViewedAt"]) <= older_than
                )
            )
        )

    watched_videos = [video for video in videos if is_watched_video(video)]

    return watched_videos


def delete_videos(watched_videos, media_type):
    """Delete watched videos and send notification"""

    def get_title(video):
        if media_type == "show":
            series = video.get("@grandparentTitle", "")
            return f"{series} - {video['@title']}"

        return video["@title"]

    def is_whitelisted(video):
        title = get_title(video)
        check = title in WHITELIST or video.get("@grandparentTitle", "") in WHITELIST
        if check:
            logging.info(I18N["whitelisted"].format(title))
        return check

    def get_size(video):
        return round(int(video["Media"]["Part"]["@size"]) / (1024 * 1024), 2)

    def delete_video(video):
        url = PLEX_BASE + video["@key"]
        size_mb = get_size(video)
        make_request(
            url=url, headers={"X-Plex-Token": PLEX_TOKEN}, request_type="delete"
        )
        return size_mb, get_title(video)

    deleted_videos = [
        delete_video(video) for video in watched_videos if not is_whitelisted(video)
    ]

    if deleted_videos:
        deleted_titles, reclaimed_mb = zip(*deleted_videos)
        reclaimed_gb = round(sum(reclaimed_mb) / 1024, 2)
        deleted_count = len(deleted_titles)

        logging.info(I18N["removed"].format(deleted_count, reclaimed_gb))
        logging.info("\n".join(deleted_titles))

        send_notification(
            deleted_titles=list(deleted_titles), reclaimed_gb=reclaimed_gb
        )

    else:
        logging.info(I18N["no_videos"])


def send_notification(deleted_titles, reclaimed_gb):
    """Handles the IFTTT request"""

    # Send notification if IFTTT URL is set correctly
    webhook_url = urllib.parse.urlparse(IFTTT_WEBHOOK)
    if webhook_url.scheme and webhook_url.netloc:
        deleted_count = len(deleted_titles)

        notification = {
            "value1": f"{I18N['removed'].format(deleted_count, reclaimed_gb)}\n"
            + "\n".join(deleted_titles)
        }
        make_request(url=IFTTT_WEBHOOK, json=notification, request_type="post")

        logging.info(I18N["notification"])
    else:
        logging.info(I18N["ifttt_error"])


def handle_request_errors(func):
    """Handle request errors"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as err:
            logging.error(err)
            return None

    return wrapper


@handle_request_errors
def make_request(**kwargs):
    """Handle requests"""

    request_url = kwargs.get("url")
    request_headers = kwargs.get("headers")
    request_json = kwargs.get("json")
    request_type = kwargs.get("request_type", "get")

    request_function = {
        "delete": requests.delete,
        "post": requests.post,
        "get": requests.get,
    }.get(request_type, requests.get)

    return request_function(
        request_url, headers=request_headers, json=request_json, timeout=10
    )


if __name__ == "__main__":
    # Check if the config argument was provided
    if input_args.config:
        update_config_file()
    elif input_args.version:
        print(f"Verily, the current installed version is: {__version__}")
    else:
        # Call the plexorcise function if the config argument is not provided
        plexorcise()
