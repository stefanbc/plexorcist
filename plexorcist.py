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


class Plexorcist:
    """Main class for Plexorcist"""

    def __init__(self):
        """Init method for Plexorcist"""

        self._set_config()
        self._set_properties()
        self._set_logging()

    def _set_config(self):
        """Read the config file and set the config dictionary"""

        # Get the absolute path of the directory containing the script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the absolute path of the INI file
        self.config_file_path = os.path.join(script_dir, "plexorcist.ini")

        # Read the config file
        self.config_file = configparser.ConfigParser()
        self.config_file.read(self.config_file_path)

        # Extract configuration values into a separate dictionary
        self.config = {
            "plex_hostname": self.config_file.get("plex", "hostname"),
            "plex_port": self.config_file.get("plex", "port"),
            "plex_token": self.config_file.get("plex", "token"),
            "plex_libraries": [
                library.strip()
                for library in self.config_file.get("plex", "libraries").split(",")
            ],
            "ifttt_webhook": self.config_file.get("plex", "ifttt_webhook"),
            "whitelist": [
                video.strip()
                for video in self.config_file.get("plex", "whitelist").split(",")
            ],
            "older_than": self._set_older_than(),
            "i18n": {
                translation: self.config_file.get("i18n", translation)
                for translation in self.config_file.options("i18n")
            },
            "log_file": os.path.join(script_dir, "plexorcist.log"),
        }

    def _set_properties(self):
        """Set the script properties"""

        self.plex_base = (
            f"http://{self.config['plex_hostname']}:{self.config['plex_port']}"
        )

    def _set_logging(self):
        """Set the logger"""

        # Create a rotating file handler with a maximum size of 1 MB
        handler = RotatingFileHandler(
            self.config["log_file"], maxBytes=1024 * 1024, backupCount=2
        )

        # Configure the logger with the rotating file handler
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[handler],
            format="%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def _set_older_than(self):
        """Handle older than time diff"""

        older_than_string = self.config_file.get("plex", "older_than").split()
        older_than_dict = {"days": 0, "hours": 0, "minutes": 0}
        time_units = {"d": "days", "h": "hours", "m": "minutes"}

        if older_than_string[0] == "0":
            return 0

        for time in older_than_string:
            unit = time[-1]
            value = int(time[:-1])
            if unit in time_units:
                older_than_dict[time_units[unit]] = value

        older_than_timedelta = timedelta(**older_than_dict)
        time_ago = datetime.now() - older_than_timedelta
        unixtime = int(time_ago.timestamp())

        return unixtime

    def update_config_file(self):
        """Update the config file via user prompt"""

        print(
            "Behold, if thou appendeth the flag 'config' unto thy command,\n"
            + "thou shalt be granted the power to update thy"
            + "configuration file with new values!\n\n"
        )

        new_config_values = {}

        # Prompt the user for new values for each option in the "plex" section
        for item in self.config_file.options("plex"):
            value_prompt = input(f"Enter the new {item} (or press enter to skip): ")
            if value_prompt:
                new_config_values[item] = value_prompt

        # Update the values in the config object
        for option, value in new_config_values.items():
            self.config_file.set("plex", option, value)

        # Write the changes back to the INI file
        with open(self.config_file_path, "w", encoding="utf-8") as configfile:
            self.config_file.write(configfile)
            logging.info("Config file has been updated with new values!")

        print(
            "\n\nVerily, I thanketh thee for thine input, forsooth,"
            + "and may thy configuration file\n"
            + "be blessed with new values that shall "
            + "bring forth great fruit in thine endeavours!"
        )

    def banish(self):
        """The banishing method"""

        library_ids = self.convert_to_library_ids(self.config["plex_libraries"])

        # Fetch the Plex data
        for library in library_ids:
            response = make_request(
                url=f"{self.plex_base}/library/sections/{library}/allLeaves",
                headers={"X-Plex-Token": self.config["plex_token"]},
            )

            # Handle videos
            self.handle_videos(response=response)

    def convert_to_library_ids(self, libraries):
        """Converts a list of library names or ids to a list of library ids"""

        available_libraries = self.get_available_libraries()

        return [
            int(library)
            if library.isdigit()
            else self.get_library_id_by_name(library, available_libraries)
            for library in libraries
            if library
        ]

    def get_available_libraries(self):
        """Returns a list of available Plex libraries"""

        response = make_request(
            url=f"{self.plex_base}/library/sections",
            headers={"X-Plex-Token": self.config["plex_token"]},
        )

        if response is not None:
            data = xmltodict.parse(response.content)
            return data["MediaContainer"]["Directory"]

        return []

    def get_library_id_by_name(self, library_name, available_libraries):
        """Returns the library ID for the given library name"""

        for section in available_libraries:
            if section["@title"].lower() == library_name.lower():
                return int(section["@key"])
        return None

    def handle_videos(self, response):
        """Handle videos"""

        if response is not None:
            data = xmltodict.parse(response.content)
            videos = data["MediaContainer"]["Video"]
            media_type = data["MediaContainer"]["@viewGroup"]

            if videos and len(videos) > 0:
                # Filter watched videos
                watched_videos = self.filter_videos(videos=videos)

                # Delete watched videos and send notification
                self.delete_videos(watched_videos=watched_videos, media_type=media_type)

    def filter_videos(self, videos):
        """Filter videos"""

        # Check if video was watched and / or is older than
        def is_watched_video(video):
            return (
                video.get("@viewCount")
                and int(video["@viewCount"]) >= 1
                and (
                    self.config["older_than"] == 0
                    or (
                        video.get("@lastViewedAt")
                        and int(video["@lastViewedAt"]) <= self.config["older_than"]
                    )
                )
            )

        watched_videos = [video for video in videos if is_watched_video(video)]

        return watched_videos

    def delete_videos(self, watched_videos, media_type):
        """Delete watched videos and send notification"""

        # Get the video title
        def get_title(video):
            if media_type == "show":
                series = video.get("@grandparentTitle", "")
                return f"{series} - {video['@title']}"

            return video["@title"]

        # Check if the video is whitelisted
        def is_whitelisted(video):
            title = get_title(video)
            check = (
                title in self.config["whitelist"]
                or video.get("@grandparentTitle", "") in self.config["whitelist"]
            )
            if check:
                logging.info(self.config["i18n"]["whitelisted"].format(title))
            return check

        # Get the video size
        def get_size(video):
            return round(int(video["Media"]["Part"]["@size"]) / (1024 * 1024), 2)

        # Delete the video
        def delete_video(video):
            url = self.plex_base + video["@key"]
            size_mb = get_size(video)
            make_request(
                url=url,
                headers={"X-Plex-Token": self.config["plex_token"]},
                request_type="delete",
            )
            return size_mb, get_title(video)

        deleted_videos = [
            delete_video(video) for video in watched_videos if not is_whitelisted(video)
        ]

        if deleted_videos:
            reclaimed_mb, deleted_titles = zip(*deleted_videos)
            reclaimed_gb = round(sum(reclaimed_mb) / 1024, 2)
            deleted_count = len(deleted_titles)

            logging.info(
                self.config["i18n"]["removed"].format(deleted_count, reclaimed_gb)
            )
            logging.info("\n".join(deleted_titles))

            self.send_notification(
                deleted_titles=list(deleted_titles), reclaimed_gb=reclaimed_gb
            )

        else:
            logging.info(self.config["i18n"]["no_videos"])

    def send_notification(self, deleted_titles, reclaimed_gb):
        """Handles the IFTTT request"""

        # Send notification if IFTTT URL is set correctly
        webhook_url = urllib.parse.urlparse(self.config["ifttt_webhook"])
        if webhook_url.scheme and webhook_url.netloc:
            deleted_count = len(deleted_titles)

            notification = {
                "value1": f"{self.config['i18n']['removed'].format(deleted_count, reclaimed_gb)}\n"
                + "\n".join(deleted_titles)
            }
            make_request(
                url=self.config["ifttt_webhook"], json=notification, request_type="post"
            )

            logging.info(self.config["i18n"]["notification"])
        else:
            logging.info(self.config["i18n"]["ifttt_error"])


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
    # Define command-line args
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action="store_true", help="update config file")
    parser.add_argument(
        "--version",
        action="store_true",
        help="prints the current installed version",
    )

    # Parse command-line args
    input_args = parser.parse_args()

    # Check if the config arg is provided
    if input_args.config:
        Plexorcist().update_config_file()
    # Check if the version arg is provided
    elif input_args.version:
        print(f"Verily, the current installed version is: {__version__}")
    else:
        # Call the banish method if the config or version args are not provided
        Plexorcist().banish()
