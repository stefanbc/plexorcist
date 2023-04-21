#!/usr/bin/env python
"""Main Plexorcist execution file!"""

import json
import urllib.parse
import logging
from logging.handlers import RotatingFileHandler
import functools
import requests
import xmltodict

# Read the JSON config file
with open("plexorcist.config.json", "r", encoding="utf8") as config_file:
    # Load the JSON data into a Python dictionary
    config = json.load(config_file)

# Set the script properties
PLEX_HOSTNAME = f"http://{config['PLEX_HOSTNAME']}:{config['PLEX_PORT']}"
PLEX_TOKEN = config["PLEX_TOKEN"]
PLEX_LIBRARY = config["PLEX_LIBRARY"]
IFTTT_WEBHOOK = config["IFTTT_WEBHOOK"]
WHITELIST = config["WHITELIST"]
I18N = config["I18N"]

# Set the log file name
LOG_FILE = "plexorcist.log"

# Create a rotating file handler with a maximum size of 1 MB
handler = RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=2)
# Configure the logger with the rotating file handler
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[handler],
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def plexorcise():
    """Main plexorcise method"""

    # Fetch the Plex data
    response = make_request(
        url=f"{PLEX_HOSTNAME}/library/sections/{PLEX_LIBRARY}/allLeaves",
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

        if videos and len(videos) > 0:
            # Filter watched videos
            watched_videos = filter_videos(videos=videos)

            # Delete watched videos and send notification
            delete_videos(watched_videos=watched_videos, media_type=media_type)


def filter_videos(videos):
    """Filter videos"""

    watched_videos = []

    if isinstance(videos, list):
        watched_videos = [
            video
            for video in videos
            if video.get("@viewCount") and int(video["@viewCount"]) >= 1
        ]
    else:
        if videos.get("@viewCount") and int(videos["@viewCount"]) >= 1:
            watched_videos.append(videos)

    return watched_videos


def delete_videos(watched_videos, media_type):
    """Delete watched videos and send notification"""

    if watched_videos and len(watched_videos) > 0:
        watched_titles = []
        reclaimed_mb = 0

        # Delete watched videos if not included in WHITELIST
        for video in watched_videos:
            series = (
                video["@grandparentTitle"] if video.get("@grandparentTitle") else ""
            )
            title = (
                f"{series} - {video['@title']}"
                if media_type == "show"
                else video["@title"]
            )
            size_bytes = int(video["Media"]["Part"]["@size"])
            size_mb = size_bytes / (1024 * 1024)

            if series not in WHITELIST or title not in WHITELIST:
                url = PLEX_HOSTNAME + video["@key"]

                watched_titles.append(title)
                reclaimed_mb += round(size_mb, 2)
                make_request(
                    url=url,
                    headers={"X-Plex-Token": PLEX_TOKEN},
                    request_type="delete",
                )
            else:
                logging.info(I18N["WHITELISTED"].format(title))

        reclaimed_gb = round(reclaimed_mb / 1024, 2)

        # Write to log file
        logging.info(I18N["REMOVED"].format(len(watched_videos), reclaimed_gb))
        logging.info("\n".join(watched_titles))

        # Send notification via IFTTT
        send_notification(
            watched_videos=watched_videos,
            watched_titles=watched_titles,
            reclaimed_gb=reclaimed_gb,
        )

    else:
        logging.info(I18N["NO_VIDEOS"])


def send_notification(watched_videos, watched_titles, reclaimed_gb):
    """Handles the IFTTT request"""

    # Send notification if IFTTT URL is set
    webhook_url = urllib.parse.urlparse(IFTTT_WEBHOOK)
    if webhook_url.scheme and webhook_url.netloc and "maker.ifttt.com" in IFTTT_WEBHOOK:
        notification = {
            "value1": f"{I18N['REMOVED'].format(len(watched_videos), reclaimed_gb)}\n"
            + "\n".join(watched_titles)
        }
        make_request(url=IFTTT_WEBHOOK, json=notification, request_type="post")

        logging.info(I18N["NOTIFICATION"])
    else:
        logging.info(I18N["IFTTT_ERROR"])


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
    plexorcise()
