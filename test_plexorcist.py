import unittest
from unittest.mock import MagicMock, patch
from plexorcist import Plexorcist


class TestPlexorcist(unittest.TestCase):

    @patch("plexorcist.utils.Utils.make_request")
    def test_handle_videos(self, mock_make_request):
        # Prepare test data
        mock_response = MagicMock()
        mock_response.content = b'<?xml version="1.0" encoding="UTF-8"?><MediaContainer viewGroup="show"><Video viewCount="1" lastViewedAt="123" grandparentTitle="Grandparent" title="Title"><Media><Part size="1024"/></Media></Video></MediaContainer>'
        mock_make_request.return_value = mock_response

        # Test handle_videos method
        plexorcist = Plexorcist()
        plexorcist.handle_videos(mock_response)

        # Assertions
        mock_make_request.assert_called_once()

    @patch("plexorcist.utils.Utils.make_request")
    def test_get_available_libraries(self, mock_make_request):
        # Prepare test data
        mock_response = MagicMock()
        mock_response.content = b'<?xml version="1.0" encoding="UTF-8"?><MediaContainer><Directory title="Movies"></Directory></MediaContainer>'
        mock_make_request.return_value = mock_response

        # Test get_available_libraries method
        plexorcist = Plexorcist()
        libraries = plexorcist.get_available_libraries()

        print(libraries)

        # Assertions
        self.assertEqual(len(libraries), 1)
        self.assertEqual(libraries[0]["@title"], "Movies")

    @patch("plexorcist.utils.Utils.make_request")
    def test_delete_videos(self, mock_make_request):
        # Prepare test data
        mock_response = MagicMock()
        mock_response.content = b'<?xml version="1.0" encoding="UTF-8"?><MediaContainer viewGroup="show"><Video viewCount="1" lastViewedAt="123" grandparentTitle="Grandparent" title="Title"><Media><Part size="1024"/></Media></Video></MediaContainer>'
        mock_make_request.return_value = mock_response

        # Test delete_videos method
        plexorcist = Plexorcist()
        plexorcist.config = {"whitelist": ["Whitelisted Title"]}
        watched_videos = [
            {
                "@title": "Title",
                "@grandparentTitle": "Grandparent",
                "@key": "/path/to/video",
                "Media": {"Part": {"@size": "1024"}},
            }
        ]
        plexorcist.delete_videos(watched_videos, "movie")

        # Assertions
        mock_make_request.assert_called_once()

    def test_filter_videos(self):
        # Test filter_videos method
        plexorcist = Plexorcist()
        videos = [
            {"@viewCount": "1", "@lastViewedAt": "123"},
            {"@viewCount": "0", "@lastViewedAt": "0"},
        ]
        watched_videos = plexorcist.filter_videos(videos)
        self.assertEqual(len(watched_videos), 1)

    def test_get_library_id_by_name(self):
        # Test get_library_id_by_name method
        plexorcist = Plexorcist()
        available_libraries = [
            {"@title": "Movies", "@key": "1"},
            {"@title": "TV Shows", "@key": "2"},
        ]
        library_id = plexorcist.get_library_id_by_name("Movies", available_libraries)
        self.assertEqual(library_id, 1)

    def test_set_older_than(self):
        # Test set_older_than method
        plexorcist = Plexorcist()
        plexorcist.config_file = MagicMock()
        plexorcist.config_file.get.return_value = "1d"
        older_than = plexorcist._set_older_than()
        self.assertGreater(older_than, 0)

    @patch("plexorcist.utils.Utils.make_request")
    def test_send_notification(self, mock_make_request):
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

    def test_get_title_show(self):
        # Test get_title method for show media type
        plexorcist = Plexorcist()
        video = {"@grandparentTitle": "Grandparent", "@title": "Title"}
        title = plexorcist.get_title(video)
        self.assertEqual(title, "Grandparent - Title")

    def test_get_title_movie(self):
        # Test get_title method for movie media type
        plexorcist = Plexorcist()
        video = {"@title": "Title"}
        title = plexorcist.get_title(video)
        self.assertEqual(title, "Title")

    def test_is_whitelisted(self):
        # Test is_whitelisted method
        plexorcist = Plexorcist()
        plexorcist.config = {"whitelist": ["Whitelisted Title"]}
        video = {"@title": "Title"}
        is_whitelisted = plexorcist.is_whitelisted(video)
        self.assertFalse(is_whitelisted)

    def test_get_size(self):
        # Test get_size method
        plexorcist = Plexorcist()
        video = {"Media": {"Part": {"@size": "1024"}}}
        size = plexorcist.get_size(video)
        self.assertEqual(size, 0.001)

    @patch("plexorcist.utils.Utils.make_request")
    def test_convert_to_library_ids(self, mock_make_request):
        # Prepare test data
        mock_response = MagicMock()
        mock_response.content = b'<?xml version="1.0" encoding="UTF-8"?><MediaContainer><Directory title="Movies" key="1"></Directory><Directory title="TV Shows" key="2"></Directory></MediaContainer>'
        mock_make_request.return_value = mock_response

        # Test convert_to_library_ids method
        plexorcist = Plexorcist()
        plexorcist.config = {"plex_base": "http://example.com", "plex_token": "token"}
        library_ids = plexorcist.convert_to_library_ids(["Movies", "TV Shows"])

        # Assertions
        self.assertEqual(library_ids, [1, 2])

    def test_get_library_id_by_name_found(self):
        # Test get_library_id_by_name method when library is found
        plexorcist = Plexorcist()
        available_libraries = [
            {"@title": "Movies", "@key": "1"},
            {"@title": "TV Shows", "@key": "2"},
        ]
        library_id = plexorcist.get_library_id_by_name("Movies", available_libraries)
        self.assertEqual(library_id, 1)

    def test_get_library_id_by_name_not_found(self):
        # Test get_library_id_by_name method when library is not found
        plexorcist = Plexorcist()
        available_libraries = [
            {"@title": "Movies", "@key": "1"},
            {"@title": "TV Shows", "@key": "2"},
        ]
        library_id = plexorcist.get_library_id_by_name("Music", available_libraries)
        self.assertIsNone(library_id)


if __name__ == "__main__":
    unittest.main()
