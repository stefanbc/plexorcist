import unittest
from unittest.mock import patch, Mock
from plexorcist import Plexorcist


class TestPlexorcist(unittest.TestCase):
    def setUp(self):
        self.plexorcist = Plexorcist()

    @patch("plexorcist.make_request")
    def test_banish(self, mock_make_request):
        mock_make_request.return_value = {"Video": [{"ratingKey": "1234"}]}
        self.plexorcist.banish()
        mock_make_request.assert_called_with(
            url=f"{self.plexorcist.config['plex_base']}/library/sections/1/allLeaves",
            headers={"X-Plex-Token": self.plexorcist.config["plex_token"]},
        )

    @patch("plexorcist.make_request")
    def test_banish_handles_none_response(self, mock_make_request):
        mock_make_request.return_value = None
        self.plexorcist.banish()
        mock_make_request.assert_called_once()

    def test_convert_to_library_ids_with_ids(self):
        libraries = ["1", "2"]
        result = self.plexorcist.convert_to_library_ids(libraries)
        self.assertEqual(result, [1, 2])

    @patch("plexorcist.Plexorcist.get_available_libraries")
    def test_convert_to_library_ids_with_names(self, mock_get_available_libraries):
        mock_get_available_libraries.return_value = {"Movies": 1, "TV Shows": 2}
        libraries = ["Movies", "TV Shows"]
        result = self.plexorcist.convert_to_library_ids(libraries)
        self.assertEqual(result, [1, 2])

    @patch("plexorcist.make_request")
    def test_handle_videos(self, mock_make_request):
        mock_make_request.return_value = {"Video": [{"ratingKey": "1234"}]}
        self.plexorcist.handle_videos(response=mock_make_request())
        self.assertIn("1234", self.plexorcist.videos_to_banish)

    def test_get_library_id_by_name(self):
        available_libraries = {"Movies": 1, "TV Shows": 2}
        result = self.plexorcist.get_library_id_by_name("TV Shows", available_libraries)
        self.assertEqual(result, 2)

    def test_get_library_id_by_name_returns_none(self):
        available_libraries = {"Movies": 1, "TV Shows": 2}
        result = self.plexorcist.get_library_id_by_name("Music", available_libraries)
        self.assertIsNone(result)
