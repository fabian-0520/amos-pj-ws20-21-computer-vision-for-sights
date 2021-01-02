import os
import unittest
from mock import patch

from sight_collector import get_sights


class SightCollectorTestcase(unittest.TestCase):
    @patch("requests.get")
    @patch.dict(os.environ, {"apikey": "abc"})
    @patch.dict(os.environ, {"maps_key": "abc"})
    def test_successful_sight_collection(self, mock_get):
        # we combine responses from both apis into one call
        rep = {"results": [{"geometry": {"location": {"lat": 0, "lng": 0}}}],
                                      "status": "OK", "features": [{"properties": {"name": "brandenburger tor"}}]}
        mock_get.return_value.json.return_value = rep
        mock_get.return_value.status_code = 200
        sights_list = get_sights("berlin", 10)
        self.assertEqual(len(sights_list), 1)
        self.assertEqual(sights_list[0], "brandenburger tor")

    def test_error_no_api_keys(self):
        sight_list = get_sights("a", 1)
        self.assertEqual(len(sight_list), 0)
        self.assertEqual(os.environ.get("apikey"), None)

    @patch.dict(os.environ, {"apikey": "abc"})
    @patch.dict(os.environ, {"maps_key": "abc"})
    def test_error_maps_wrong_response(self):
        sight_list = get_sights("a", 1)
        self.assertEqual(len(sight_list), 0)
        self.assertEqual(os.environ.get("apikey"), "abc")
        self.assertEqual(os.environ.get("maps_key"), "abc")

    if __name__ == '__main__':
        unittest.main()
