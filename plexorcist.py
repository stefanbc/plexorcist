#!/usr/bin/env python

import os
import requests
import json
import xmltodict
import urllib.parse
from datetime import datetime

# Read the JSON config file
with open('plexorcist.config.json', 'r') as config_file:
    # Load the JSON data into a Python dictionary
    config = json.load(config_file)

# Set the script properties
PLEX_HOSTNAME = config['PLEX_HOSTNAME']
PLEX_TOKEN = config['PLEX_TOKEN']
PLEX_LIBRARY = config['PLEX_LIBRARY']
IFTTT_WEBHOOK = config['IFTTT_WEBHOOK']
BLACKLIST = config['BLACKLIST']

# Set the log file name
LOG_FILE = 'plexorcist.log'
LOG_FILE_MAX_SIZE = 2000000 # 2 MB
LOG_FILE_CURRENT_SIZE = os.path.getsize(LOG_FILE)

# Main plexorcise method
def plexorcise():
    # Check if the log file is larger than LOG_FILE_MAX_SIZE and empty it
    if LOG_FILE_CURRENT_SIZE > LOG_FILE_MAX_SIZE:
        with open(LOG_FILE, "w") as log_file:
            log_file.truncate(0)

    # Set the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fetch the Plex data
    response = requests.get(f"{PLEX_HOSTNAME}/library/sections/{int(PLEX_LIBRARY)}/allLeaves", headers={"X-Plex-Token": PLEX_TOKEN})
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

            # Delete watched videos if not included in blacklist
            for video in watched_videos:
                series = video['@grandparentTitle']
                title = f"{video['@grandparentTitle']} - {video['@title']}"

                if series not in BLACKLIST:
                    url = PLEX_HOSTNAME + video['@key']

                    watched_titles.append(title)
                    requests.delete(url, headers={"X-Plex-Token": PLEX_TOKEN})
                else:
                    with open(LOG_FILE, 'a') as log_file:
                        log_file.write(f'{timestamp} - {title} is blacklisted!\n')

            # Write to log file
            with open(LOG_FILE, 'a') as log_file:
                log_file.write(f"{timestamp} - {len(watched_videos)} watched episodes were removed:\n")
                log_file.write('\n'.join(watched_titles))
                log_file.write('\n')

            # Send notification if IFTTT url is set
            webhook_url = urllib.parse.urlparse(IFTTT_WEBHOOK)
            if webhook_url.scheme and webhook_url.netloc:
                notification = {
                    'value1': f"{len(watched_videos)} watched episodes were removed!\n" + '\n'.join(watched_titles)
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

if __name__ == '__main__':
    plexorcise()