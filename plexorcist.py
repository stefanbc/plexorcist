#!/usr/bin/env python
"""Main Plexorcist execution file!"""

import os
import sys
import json
import urllib.parse
from datetime import datetime
import requests
import xmltodict

# Check if cast is triggered
CAST = "--cast" in sys.argv

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

# Create file if it's missing
if not os.path.isfile(LOG_FILE):
    # Create an empty file
    with open(LOG_FILE, "w", encoding="utf8") as log_file:
        log_file.close()

# Size check
LOG_FILE_MAX_SIZE = 2000000  # 2 MB
LOG_FILE_CURRENT_SIZE = os.path.getsize(LOG_FILE)

# Check if the log file is larger than LOG_FILE_MAX_SIZE and empty it
if LOG_FILE_CURRENT_SIZE > LOG_FILE_MAX_SIZE:
    with open(LOG_FILE, "w", encoding="utf8") as log_file:
        log_file.truncate(0)

# Set the current timestamp
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def plexorcise():
    """Main plexorcise method"""

    # Fetch the Plex data
    response = make_request(
        url=f"{PLEX_HOSTNAME}/library/sections/{PLEX_LIBRARY}/allLeaves",
        headers={"X-Plex-Token": PLEX_TOKEN},
    )

    if response is not None:
        data = xmltodict.parse(response)
        videos = data["MediaContainer"]["Video"]
        media_type = data["MediaContainer"]["@viewGroup"]

        if videos and len(videos) > 0:
            watched_videos = []

            # Filter watched videos
            if isinstance(videos, list):
                watched_videos = [
                    video
                    for video in videos
                    if video.get("@viewCount") and int(video["@viewCount"]) >= 1
                ]
            else:
                if videos.get("@viewCount") and int(videos["@viewCount"]) >= 1:
                    watched_videos.append(videos)

            # Delete watched videos and send notification
            if watched_videos and len(watched_videos) > 0:
                watched_titles = []
                space_reclaimed_in_mb = 0

                # Delete watched videos if not included in WHITELIST
                for video in watched_videos:
                    series = (
                        video["@grandparentTitle"]
                        if video.get("@grandparentTitle")
                        else ""
                    )
                    title = (
                        f"{series} - {video['@title']}"
                        if media_type == "show"
                        else video["@title"]
                    )
                    size_in_bytes = int(video["Media"]["Part"]["@size"])
                    size_in_mb = size_in_bytes / (1024 * 1024)

                    if series not in WHITELIST or title not in WHITELIST:
                        url = PLEX_HOSTNAME + video["@key"]

                        watched_titles.append(title)
                        space_reclaimed_in_mb += round(size_in_mb, 2)
                        make_request(
                            url=url,
                            headers={"X-Plex-Token": PLEX_TOKEN},
                            request_type="delete",
                        )
                    else:
                        with open(LOG_FILE, "a", encoding="utf8") as log_file:
                            log_file.write(
                                f"{I18N['WHITELISTED'].format(TIMESTAMP, title)}\n"
                            )

                space_reclaimed_in_gb = round(space_reclaimed_in_mb / 1024, 2)

                # Write to log file
                with open(LOG_FILE, "a", encoding="utf8") as log_file:
                    log_file.write(
                        f"{I18N['WATCHED_VIDES_REMOVED'].format(TIMESTAMP, len(watched_videos), space_reclaimed_in_gb)}\n"
                    )
                    log_file.write("\n".join(watched_titles))
                    log_file.write("\n")

                # Send notification if IFTTT URL is set
                webhook_url = urllib.parse.urlparse(IFTTT_WEBHOOK)
                if (
                    "maker.ifttt.com" in IFTTT_WEBHOOK
                    and webhook_url.scheme
                    and webhook_url.netloc
                ):
                    notification = {
                        "value1": f"{I18N['WATCHED_VIDES_REMOVED'].format(TIMESTAMP, len(watched_videos), space_reclaimed_in_gb)}\n"
                        + "\n".join(watched_titles)
                    }
                    make_request(
                        url=IFTTT_WEBHOOK, json=notification, request_type="post"
                    )

                    with open(LOG_FILE, "a", encoding="utf8") as log_file:
                        log_file.write(f"{I18N['NOTIFICATION'].format(TIMESTAMP)}\n")
                else:
                    with open(LOG_FILE, "a", encoding="utf8") as log_file:
                        log_file.write(f"{I18N['IFTTT_ERROR'].format(TIMESTAMP)}\n")
            else:
                with open(LOG_FILE, "a", encoding="utf8") as log_file:
                    log_file.write(f"{I18N['NO_VIDEOS'].format(TIMESTAMP)}\n")

            # Open the log file in read mode
            if CAST:
                with open(LOG_FILE, "r", encoding="utf8") as log_file:
                    # Read the contents of the log file
                    contents = log_file.read()
                    # Print the contents to the console
                    print(contents)


def make_request(**kwargs):
    """Make a request method"""

    request_url = kwargs.get("url")
    request_headers = kwargs.get("headers")
    request_json = kwargs.get("json")
    request_type = kwargs.get("request_type", "get")

    exception = None
    response = None

    try:
        if request_type == "delete":
            response = requests.delete(request_url, headers=request_headers, timeout=10)
        elif request_type == "post":
            response = requests.post(request_url, json=request_json, timeout=10)
        else:
            response = requests.get(request_url, headers=request_headers, timeout=10)
        response.raise_for_status()  # Raise an exception for non-2xx responses
    except requests.exceptions.HTTPError as err:
        exception = f"{I18N['HTTPError'].format(err)}"
    except requests.exceptions.ConnectionError as err:
        exception = f"{I18N['ConnectionError'].format(err)}"
    except requests.exceptions.Timeout as err:
        exception = f"{I18N['Timeout'].format(err)}"
    except requests.exceptions.RequestException as err:
        exception = f"{I18N['RequestException'].format(err)}"

    if exception != "":
        if CAST:
            print(exception)
        else:
            with open(LOG_FILE, "a", encoding="utf8") as log_file:
                log_file.write(f"{TIMESTAMP} - {exception}\n")

        return exception

    return response.content


if __name__ == "__main__":
    plexorcise()
