#!/usr/bin/env python

import os
import sys
import requests
import json
import xmltodict
import urllib.parse
from datetime import datetime

# Check if cast is triggered
cast = "--cast" in sys.argv

# Read the JSON config file
with open('plexorcist.config.json', 'r') as config_file:
    # Load the JSON data into a Python dictionary
    config = json.load(config_file)

# Set the script properties
PLEX_HOSTNAME = f"http://{config['PLEX_HOSTNAME']}:{config['PLEX_PORT']}"
PLEX_TOKEN = config['PLEX_TOKEN']
PLEX_LIBRARY = config['PLEX_LIBRARY']
IFTTT_WEBHOOK = config['IFTTT_WEBHOOK']
WHITELIST = config['WHITELIST']

# Set the log file name
LOG_FILE = 'plexorcist.log'

# Create file if it's missing
if not os.path.isfile(LOG_FILE):
    # Create an empty file
    open(LOG_FILE, 'w').close()

# Size check
LOG_FILE_MAX_SIZE = 2000000 # 2 MB
LOG_FILE_CURRENT_SIZE = os.path.getsize(LOG_FILE)

# Check if the log file is larger than LOG_FILE_MAX_SIZE and empty it
if LOG_FILE_CURRENT_SIZE > LOG_FILE_MAX_SIZE:
    with open(LOG_FILE, "w") as log_file:
        log_file.truncate(0)

# Main plexorcise method
def plexorcise():
    # Set the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fetch the Plex data
    response = requests.get(f"{PLEX_HOSTNAME}/library/sections/{PLEX_LIBRARY}/allLeaves", headers={"X-Plex-Token": PLEX_TOKEN})
    data = xmltodict.parse(response.content)
    videos = data['MediaContainer']['Video']

    if videos:
        watched_videos = []

        # Filter watched videos
        if isinstance(videos, list):
            watched_videos = [video for video in videos if video.get('@viewCount') and int(video['@viewCount']) >= 1]
        else:
            if videos.get('@viewCount') and int(videos['@viewCount']) >= 1:
                watched_videos.append(videos)

        # Delete watched videos and send notification
        if watched_videos:
            watched_titles = []
            space_reclaimed_in_mb = 0

            # Delete watched videos if not included in WHITELIST
            for video in watched_videos:
                series = video['@grandparentTitle']
                title = f"{video['@grandparentTitle']} - {video['@title']}"
                size_in_bytes = int(video['Media']['Part']['@size'])
                size_in_mb = size_in_bytes / (1024 * 1024)

                if series not in WHITELIST:
                    url = PLEX_HOSTNAME + video['@key']

                    watched_titles.append(title)
                    space_reclaimed_in_mb += round(size_in_mb, 2)
                    requests.delete(url, headers={"X-Plex-Token": PLEX_TOKEN})
                else:
                    with open(LOG_FILE, 'a') as log_file:
                        log_file.write(f'{timestamp} - {title} is whitelisted!\n')

            space_reclaimed_in_gb = round(space_reclaimed_in_mb / 1024, 2)

            # Write to log file
            with open(LOG_FILE, 'a') as log_file:
                log_file.write(f"{timestamp} - {len(watched_videos)} watched episodes were removed and {space_reclaimed_in_gb} GB reclaimed:\n")
                log_file.write('\n'.join(watched_titles))
                log_file.write('\n')

            # Send notification if IFTTT url is set
            webhook_url = urllib.parse.urlparse(IFTTT_WEBHOOK)
            if "maker.ifttt.com" in IFTTT_WEBHOOK and webhook_url.scheme and webhook_url.netloc:
                notification = {
                    'value1': f"{len(watched_videos)} watched episodes were removed and {space_reclaimed_in_gb} GB reclaimed:\n" + '\n'.join(watched_titles)
                }
                requests.post(IFTTT_WEBHOOK, json=notification)

                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f'{timestamp} - Notification sent!\n')
            else:
                with open(LOG_FILE, 'a') as log_file:
                    log_file.write(f'{timestamp} - IFTTT Webhook URL not set!\n')
        else:
            with open(LOG_FILE, 'a') as log_file:
                log_file.write(f'{timestamp} - No videos to delete!\n')

        # Open the log file in read mode
        if cast:
            with open(LOG_FILE, 'r') as log_file:
                # Read the contents of the log file
                contents = log_file.read()
                # Print the contents to the console
                print(contents)

if __name__ == '__main__':
    plexorcise()