#!/usr/bin/env python
"""Test the main Plexorcist execution file!"""

import unittest
from unittest.mock import MagicMock, patch
from plexorcist import Plexorcist


class TestPlexorcist(unittest.TestCase):
    """The main test class for unit tests

    Args:
        unittest (module): Single test cases
    """

    def test_set_older_than(self):
        """Test for the _set_older_than method"""

        # Test set_older_than method
        plexorcist = Plexorcist()
        plexorcist.config_file = MagicMock()
        plexorcist.config_file.get.return_value = "1d"
        # pylint: disable=protected-access
        older_than = plexorcist._set_older_than()

        # Assertions
        self.assertGreater(older_than, 0)

    @patch("plexorcist.utils.Utils.make_request")
    def test_convert_to_library_ids(self, mock_make_request):
        """Test for the conver_to_library_ids

        Args:
            mock_make_request (method): Mock the make_request method
        """

        # Prepare test data
        mock_response = MagicMock()
        mock_response.content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b"<MediaContainer>"
            b'<Directory title="Cinema" key="1"></Directory>'
            b'<Directory title="Series" key="2"></Directory>'
            b"</MediaContainer>"
        )
        mock_make_request.return_value = mock_response

        # Test convert_to_library_ids method
        plexorcist = Plexorcist()
        plexorcist.config = {"plex_base": "http://example.com", "plex_token": "token"}
        library_ids = plexorcist.convert_to_library_ids(["Cinema", "Series"])

        # Assertions
        self.assertEqual(library_ids, [1, 2])

    @patch("plexorcist.utils.Utils.make_request")
    def test_get_available_libraries(self, mock_make_request):
        """Test for the get_available_libraries method

        Args:
            mock_make_request (method): Mock the make_request method
        """

        # Prepare test data
        mock_response = MagicMock()
        mock_response.content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b"<MediaContainer>"
            b'<Directory title="Cinema"></Directory>'
            b'<Directory title="Series"></Directory>'
            b"</MediaContainer>"
        )
        mock_make_request.return_value = mock_response

        # Test get_available_libraries method
        plexorcist = Plexorcist()
        libraries = plexorcist.get_available_libraries()

        # Assertions
        self.assertEqual(len(libraries), 2)
        self.assertEqual(libraries[0]["@title"], "Cinema")

    def test_get_library_id_by_name(self):
        """Test for the get_library_id_by_name method"""

        # Prepare test data
        plexorcist = Plexorcist()
        available_libraries = [
            {"@title": "Cinema", "@key": "1"},
            {"@title": "Series", "@key": "2"},
        ]
        library_id = plexorcist.get_library_id_by_name("Cinema", available_libraries)

        # Assertions
        self.assertEqual(library_id, 1)

    def test_get_library_id_by_name_found(self):
        """Test for the get_library_id_by_name when name is found"""

        # Prepare test data
        available_libraries = [
            {"@title": "Cinema", "@key": "1"},
            {"@title": "Series", "@key": "2"},
        ]

        # Test get_library_id_by_name method when library is found
        plexorcist = Plexorcist()
        library_id = plexorcist.get_library_id_by_name("Cinema", available_libraries)

        # Assertions
        self.assertEqual(library_id, 1)

    def test_get_library_id_by_name_not_found(self):
        """Test for the get_library_id_by_name when name is not found"""

        # Prepare test data
        available_libraries = [
            {"@title": "Cinema", "@key": "1"},
            {"@title": "Series", "@key": "2"},
        ]

        # Test get_library_id_by_name method when library is not found
        plexorcist = Plexorcist()
        library_id = plexorcist.get_library_id_by_name("Music", available_libraries)

        # Assertions
        self.assertIsNone(library_id)

    @patch("plexorcist.utils.Utils.make_request")
    def test_handle_videos(self, mock_make_request):
        """Test for the handle_videos method

        Args:
            mock_make_request (method): Mock the make_request method
        """

        # Prepare test data
        mock_response = MagicMock()
        mock_response.content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<MediaContainer viewGroup="show">'
            b'<Video key="1" viewCount="1" lastViewedAt="1" grandparentTitle="GPT" title="Title">'
            b"<Media>"
            b'<Part size="1024"/>'
            b"</Media>"
            b"</Video>"
            b"</MediaContainer>"
        )
        mock_make_request.return_value = mock_response

        # Test handle_videos method
        plexorcist = Plexorcist()
        plexorcist.pushbullet = MagicMock()
        plexorcist.handle_videos(mock_response)

        # Assertions
        mock_make_request.assert_called_once()

    def test_filter_videos(self):
        """Test for the filter_videos method"""

        # Prepare test data
        videos = [
            {"@viewCount": "1", "@lastViewedAt": "123"},
            {"@viewCount": "0", "@lastViewedAt": "0"},
        ]

        # Test filter_videos method
        plexorcist = Plexorcist()
        watched_videos = plexorcist.filter_videos(videos)

        # Assertions
        self.assertEqual(len(watched_videos), 1)

    def test_get_title_show(self):
        """Test for the get_title method for media type show"""

        # Prepare test data
        video = {"@grandparentTitle": "Grandparent", "@title": "Title"}

        # Test get_title method for show media type
        plexorcist = Plexorcist()
        title = plexorcist.get_title(video, "show")

        # Assertions
        self.assertEqual(title, "Grandparent - Title")

    def test_get_title_movie(self):
        """Test for get_title method for media type movie"""

        # Prepare test data
        video = {"@title": "Title", "@grandparentTitle": "Series 1"}

        # Test get_title method for movie media type
        plexorcist = Plexorcist()
        title = plexorcist.get_title(video, "show")

        # Assertions
        self.assertEqual(title, "Series 1 - Title")

    def test_is_whitelisted(self):
        """Test for the is_whitelisted method"""

        # Prepare test data
        video = {"@title": "Title"}

        # Test is_whitelisted method
        plexorcist = Plexorcist()
        plexorcist.config = {"whitelist": ["Whitelisted Title"]}
        is_whitelisted = plexorcist.is_whitelisted(video, "show")

        # Assertions
        self.assertFalse(is_whitelisted)

    def test_get_size(self):
        """Test for the get_size method"""

        # Prepare test data
        video = {"Media": [{"Part": [{"@size": "1024"}]}]}

        # Test get_size method
        plexorcist = Plexorcist()
        size = plexorcist.get_size(video)

        # Assertions
        self.assertEqual(size, 0.0)

    @patch("plexorcist.utils.Utils.make_request")
    def test_delete_videos(self, mock_make_request):
        """Test for the delete_videos method

        Args:
            mock_make_request (method): Mock the make_request method
        """

        # Prepare test data
        mock_response = MagicMock()
        mock_response.content = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<MediaContainer viewGroup="show">'
            b'<Video viewCount="1" lastViewedAt="123" grandparentTitle="Grandparent" title="Title">'
            b"<Media>"
            b'<Part size="1024"/>'
            b"</Media>"
            b"</Video>"
            b"</MediaContainer>"
        )
        mock_make_request.return_value = mock_response
        watched_videos = [
            {
                "@title": "Title",
                "@grandparentTitle": "Grandparent",
                "@key": "/path/to/video",
                "Media": [{"Part": [{"@size": "1024"}]}],
            }
        ]

        # Test delete_videos method
        plexorcist = Plexorcist()
        plexorcist.config = {
            "plex_base": "http://example.com",
            "plex_token": "token",
            "ifttt_webhook": "",
            "i18n": {
                "removed": "Removed {0} videos, reclaimed {1} GB",
                "notification": "Notification sent",
                "ifttt_error": "IFTTT webhook error",
            },
            "whitelist": ["Whitelisted Title"],
        }
        plexorcist.pushbullet = MagicMock()
        plexorcist.delete_videos(watched_videos, "movie")

        # Assertions
        mock_make_request.assert_called_once()

    @patch("plexorcist.utils.Utils.make_request")
    def test_send_notification(self, mock_make_request):
        """Test for the send_notification method

        Args:
            mock_make_request (method): Mock the make_request method
        """
        # Prepare test data
        mock_response = MagicMock()
        mock_response.content = b""
        mock_make_request.return_value = mock_response

        # Test send_notification method
        plexorcist = Plexorcist()
        plexorcist.config = {
            "ifttt_webhook": "https://ifttt.com/webhook",
            "i18n": {
                "removed": "Removed {0} videos, reclaimed {1} GB",
                "notification": "Notification sent",
                "ifttt_error": "IFTTT webhook error",
            },
        }
        plexorcist.pushbullet = MagicMock()
        plexorcist.send_notification(["Video 1", "Video 2"], 0.5)

        # Assertions
        mock_make_request.assert_called_once()


if __name__ == "__main__":
    unittest.main()
