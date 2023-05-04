"""Utilities file"""

import csv
import os
from datetime import datetime
import logging
import requests


class Utils:
    """Utilities class"""

    def __init__(self):
        """Init method for the utilities class"""

        # Get the current date time
        self.current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def write_to_csv(self, num_deleted, gb_reclaimed, csv_path):
        """Writes data to a CSV file"""

        # Create the header row if the file doesn't exist
        file_exists = os.path.isfile(csv_path)
        fieldnames = ["Timestamp", "Number of Shows Deleted", "GB of Space Reclaimed"]

        with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()

            # Write the data row
            writer.writerow(
                {
                    "Timestamp": self.current_datetime,
                    "Number of Shows Deleted": num_deleted,
                    "GB of Space Reclaimed": gb_reclaimed,
                }
            )

        logging.info("Report file has been updated with new values!")

    def handle_request_errors(self, func, *args, **kwargs):
        """Handle request errors"""

        try:
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as err:
            logging.error(err)
            return None

    def make_request(self, **kwargs):
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

        return self.handle_request_errors(
            request_function,
            url=request_url,
            headers=request_headers,
            json=request_json,
            timeout=10,
        )
