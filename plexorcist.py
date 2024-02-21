#!/usr/bin/env python
"""Main Plexorcist execution file!"""

__version__ = "1.3.6"

import os
import argparse
import configparser
import re
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import urllib.parse
import xmltodict
from pushbullet import Pushbullet
from utils import utils


class Plexorcist:
    """Main class for Plexorcist"""

    def __init__(self):
        """Init method for Plexorcist"""

        self.util = utils.Utils()

        self._set_files()
        self._set_config()
        self._set_logging()

        # Check if the Pushbullet key has been set before making requests
        match = re.match(r"^[A-Za-z0-9_.]+", self.config["pushbullet_key"])

        if match:
            self.pushbullet = Pushbullet(self.config["pushbullet_key"])

    def _set_files(self):
        """Set all needed file paths and read config file"""

        # Get the absolute path of the directory containing the script
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the absolute path of the INI file
        self.config_file_path = os.path.join(self.script_dir, "plexorcist.ini")

        # Construct the absolute path of the reports file
        self.reports_file_path = os.path.join(self.script_dir, "plexorcist_report.csv")

        # Read the config file
        self.config_file = configparser.ConfigParser()
        self.config_file.read(self.config_file_path)

    def _set_config(self):
        """Set the config dictionary"""

        # Extract configuration values into a separate dictionary
        hostname = self.config_file.get("plex", "hostname")
        port = self.config_file.get("plex", "port")

        self.config = {
            "plex_base": f"http://{hostname}:{port}",
            "plex_token": self.config_file.get("plex", "token"),
            "plex_libraries": [
                library.strip()
                for library in self.config_file.get("plex", "libraries").split(",")
            ],
            "ifttt_webhook": self.config_file.get("plex", "ifttt_webhook"),
            "pushbullet_key": self.config_file.get("plex", "pushbullet_key"),
            "whitelist": [
                video.strip()
                for video in self.config_file.get("plex", "whitelist").split(",")
            ],
            "older_than": self._set_older_than(),
            "i18n": {
                translation: self.config_file.get("i18n", translation)
                for translation in self.config_file.options("i18n")
            },
        }

    def _set_logging(self):
        """Set the logger"""

        # Create a rotating file handler with a maximum size of 1 MB
        handler = RotatingFileHandler(
            os.path.join(self.script_dir, "plexorcist.log"),
            maxBytes=1024 * 1024,
            backupCount=2,
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

        time_ago = datetime.now() - timedelta(**older_than_dict)
        unixtime = int(time_ago.timestamp())

        return unixtime

    def update_config_file(self):
        """Update the config file via user prompt"""

        print(
            "\n\nBehold, if thou appendeth the flag 'config' unto thy command,\n"
            + "thou shalt be granted the power to update thy "
            + "configuration file with new values!\n"
        )

        new_config_values = {}

        # Prompt the user for new values for each option in the "plex" section
        for item in self.config_file.options("plex"):
            try:
                value_prompt = input(
                    f"\nEnter the new {item} (or press enter to skip): "
                )
                if value_prompt:
                    new_config_values[item] = value_prompt
            except KeyboardInterrupt:
                print("\n\nThou hast interrupted the configuration of Plexorcist!")
                break

        # Update the values in the config object
        if new_config_values:
            for option, value in new_config_values.items():
                self.config_file.set("plex", option, value)

            # Write the changes back to the INI file
            with open(self.config_file_path, "w", encoding="utf-8") as configfile:
                self.config_file.write(configfile)
                logging.info("Config file has been updated with new values!")
        else:
            logging.info("No changes made to the config file.")

        print(
            "\n\nI thanketh thee for thine input, forsooth, "
            + "and may thy configuration file\n"
            + "be blessed with new values that shall "
            + "bring forth great fruit in thine endeavours!\n\n"
        )

    def banish(self):
        """The banishing method"""

        # Check if the Plex Token has been set before making requests
        match = re.match(r"^[A-Za-z0-9_]+", self.config["plex_token"])

        if not match:
            self.update_config_file()
            return

        # Convert the libraries to ids
        library_ids = self.convert_to_library_ids(self.config["plex_libraries"])

        # Fetch the Plex data
        for library in library_ids:
            response = self.util.make_request(
                url=f'{self.config["plex_base"]}/library/sections/{library}/allLeaves',
                headers={"X-Plex-Token": self.config["plex_token"]},
            )

            # Handle videos
            if response is not None:
                self.handle_videos(response=response)

    def convert_to_library_ids(self, libraries):
        """Converts a list of library names or ids to a list of library ids"""

        available_libraries = self.get_available_libraries()

        return [
            (
                int(library)
                if library.isdigit()
                else self.get_library_id_by_name(library, available_libraries)
            )
            for library in libraries
            if library
        ]

    def get_available_libraries(self):
        """Returns a list of available Plex libraries"""

        response = self.util.make_request(
            url=f'{self.config["plex_base"]}/library/sections',
            headers={"X-Plex-Token": self.config["plex_token"]},
        )

        if response is not None:
            data = xmltodict.parse(response.content, force_list=True)
            return data["MediaContainer"][0]["Directory"]

        return []

    def get_library_id_by_name(self, library_name, available_libraries):
        """Returns the library ID for the given library name"""

        for section in available_libraries:
            if section["@title"].lower() == library_name.lower():
                return int(section["@key"])
        return None

    def handle_videos(self, response):
        """Handle videos"""

        data = xmltodict.parse(response.content, force_list=True)
        videos = data["MediaContainer"][0]["Video"]
        media_type = data["MediaContainer"][0]["@viewGroup"]

        if videos and len(videos) > 0:
            # Filter watched videos
            watched_videos = self.filter_videos(videos)

            # Delete watched videos and send notification
            self.delete_videos(watched_videos, media_type)

    def filter_videos(self, videos):
        """Filter videos"""

        # Check if video was watched and / or is older than
        def is_watched_video(video):
            return (
                isinstance(video)
                and video.get("@viewCount")
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

    def get_title(self, video, media_type):
        """Get the video title"""

        if media_type == "show":
            series = video.get("@grandparentTitle", "")
            return f"{series} - {video['@title']}"

        return video["@title"]

    def is_whitelisted(self, video, media_type):
        """Check if the video is whitelisted"""

        title = self.get_title(video, media_type)
        check = (
            title in self.config["whitelist"]
            or video.get("@grandparentTitle", "") in self.config["whitelist"]
        )
        if check:
            logging.info(self.config["i18n"]["whitelisted"].format(title))
        return check

    def get_size(self, video):
        """Get the video size"""

        return round(int(video["Media"][0]["Part"][0]["@size"]) / (1024 * 1024), 2)

    def delete_video(self, video, media_type):
        """Delete the video"""

        self.util.make_request(
            url=self.config["plex_base"] + video["@key"],
            headers={"X-Plex-Token": self.config["plex_token"]},
            request_type="delete",
        )
        return self.get_size(video), self.get_title(video, media_type)

    def delete_videos(self, watched_videos, media_type):
        """Delete watched videos and send notification"""

        deleted_videos = [
            self.delete_video(video, media_type)
            for video in watched_videos
            if not self.is_whitelisted(video, media_type)
        ]

        if deleted_videos:
            reclaimed_mb, deleted_titles = zip(*deleted_videos)
            reclaimed_gb = round(sum(reclaimed_mb) / 1024, 2)
            deleted_count = len(deleted_titles)

            logging.info(
                self.config["i18n"]["removed"].format(deleted_count, reclaimed_gb)
            )
            logging.info("\n".join(deleted_titles))

            self.util.write_to_csv(
                num_deleted=deleted_count,
                gb_reclaimed=reclaimed_gb,
                csv_path=self.reports_file_path,
            )

            self.send_notification(
                deleted_titles=list(deleted_titles), reclaimed_gb=reclaimed_gb
            )
        else:
            logging.info(self.config["i18n"]["no_videos"])

            self.util.write_to_csv(
                num_deleted=0,
                gb_reclaimed=0,
                csv_path=self.reports_file_path,
            )

    def send_notification(self, deleted_titles, reclaimed_gb):
        """Handles the IFTTT / Pushbullet requests"""

        deleted_count = len(deleted_titles)
        payload = (
            f"{self.config['i18n']['removed'].format(deleted_count, reclaimed_gb)}\n"
            + "\n".join(deleted_titles)
        )

        # Send notification if IFTTT URL is set correctly
        webhook_url = urllib.parse.urlparse(self.config["ifttt_webhook"])
        if webhook_url.scheme and webhook_url.netloc:
            self.util.make_request(
                url=self.config["ifttt_webhook"],
                json={"value1": payload},
                request_type="post",
            )

            logging.info(self.config["i18n"]["notification"])
        else:
            logging.info(self.config["i18n"]["ifttt_error"])

        # Send notification via Pushbullet
        if self.pushbullet:
            self.pushbullet.push_note("Plexorcist", payload)


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
