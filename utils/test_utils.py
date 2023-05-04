"""Utils testing file!"""

import os
import unittest
from unittest.mock import call, patch, MagicMock
import requests
from utils import utils


class TestUtils(unittest.TestCase):
    """Test class for Utils"""

    def setUp(self):
        self.utils = utils.Utils()

    def test_write_to_csv(self):
        """Test write_to_csv method."""

        test_csv_path = "test.csv"
        self.utils.write_to_csv(5, 10.5, test_csv_path)

        with open(test_csv_path, "r", encoding="utf-8") as csv_file:
            csv_contents = csv_file.read()

        self.assertIn("Timestamp", csv_contents)
        self.assertIn("Number of Shows Deleted", csv_contents)
        self.assertIn("GB of Space Reclaimed", csv_contents)
        self.assertIn(str(self.utils.current_datetime), csv_contents)
        self.assertIn("5", csv_contents)
        self.assertIn("10.5", csv_contents)

        # Cleanup
        os.remove(test_csv_path)

    @patch("requests.get")
    def test_handle_request_errors_when_request_succeeds(self, mock_get):
        """Test handle_request_errors when the request succeeds"""

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        response = self.utils.handle_request_errors(mock_get, "http://example.com")

        self.assertIsNotNone(response)
        mock_get.assert_called_once_with("http://example.com")

    @patch("requests.get")
    def test_handle_request_errors_when_request_raises_exception(self, mock_get):
        """Test handle_request_errors when the request raises an exception"""

        mock_get.side_effect = requests.exceptions.RequestException("Error message")

        response = self.utils.handle_request_errors(mock_get, "http://example.com")

        self.assertIsNone(response)
        mock_get.assert_called_once_with("http://example.com")

    @patch.object(utils.Utils, "handle_request_errors")
    def test_make_request_when_request_succeeds(self, mock_handle_request_errors):
        """Test make_request when the request succeeds"""

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_handle_request_errors.return_value = mock_response

        response = self.utils.make_request(url="http://example.com", request_type="get")

        self.assertIsNotNone(response)

        # Verify that handle_request_errors was called with the correct arguments
        expected_call = call(
            requests.get,
            url="http://example.com",
            headers=None,
            json=None,
            timeout=10,
        )
        self.assertIn(expected_call, mock_handle_request_errors.call_args_list)

    @patch.object(utils.Utils, "handle_request_errors")
    def test_make_request_when_request_raises_exception(
        self, mock_handle_request_errors
    ):
        """Test make_request when the request raises an exception"""

        mock_handle_request_errors.return_value = None

        response = self.utils.make_request(url="http://example.com", request_type="get")

        self.assertIsNone(response)

        # Verify that handle_request_errors was called with the correct arguments
        expected_call = call(
            requests.get,
            url="http://example.com",
            headers=None,
            json=None,
            timeout=10,
        )
        self.assertIn(expected_call, mock_handle_request_errors.call_args_list)


if __name__ == "__main__":
    unittest.main()
