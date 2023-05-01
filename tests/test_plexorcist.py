#!/usr/bin/env python
"""Main Plexorcist testing file!"""

import unittest
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET
from plexorcist import Plexorcist


class TestPlexorcist(unittest.TestCase):
    """Main test class"""

    def test_update_config_file(self):
        """Test the update config file method"""

        # Mock input function
        with patch("builtins.input", side_effect=["localhost", "32400", "token"]):
            Plexorcist().update_config_file()

        # Check that config file was updated
        with open("plexorcist.ini", "r", encoding="utf-8") as f:
            config = f.read()
            self.assertIn("localhost", config)
            self.assertIn("32400", config)
            self.assertIn("token", config)

    def test_handle_videos(self):
        """Test the handle videos method"""

        # Mock make_request function
        response = MagicMock()
        response.content = """
            <MediaContainer>
                <Video viewCount="0"></Video>
                <Video viewCount="1" lastViewedAt="1591946823"></Video>
                <Video viewCount="1" lastViewedAt="1619714823"></Video>
            </MediaContainer>
        """
        with patch("requests.get", return_value=response):
            with patch("plexorcist.delete_videos") as mock_delete_videos:
                Plexorcist().handle_videos(response)

                # Check that delete_videos is called with the correct arguments
                mock_delete_videos.assert_called_once_with(
                    watched_videos=[
                        ET.fromstring(
                            '<Video viewCount="1" lastViewedAt="1619714823"></Video>'
                        )
                    ],
                    media_type=None,
                )

    def test_filter_videos(self):
        """Test the filter videos method"""

        videos = [
            ET.fromstring('<Video viewCount="0"></Video>'),
            ET.fromstring('<Video viewCount="1" lastViewedAt="1619714823"></Video>'),
            ET.fromstring('<Video viewCount="1" lastViewedAt="1619710823"></Video>'),
        ]

        # Test when older_than is set to "0 days"
        with patch("plexorcist.config.get", return_value="0 days"):
            watched_videos = Plexorcist().filter_videos(videos)
            self.assertEqual(watched_videos, [videos[1], videos[2]])

        # Test when older_than is set to "1 day"
        with patch("plexorcist.config.get", return_value="1 day"):
            watched_videos = Plexorcist().filter_videos(videos)
            self.assertEqual(watched_videos, [videos[2]])
