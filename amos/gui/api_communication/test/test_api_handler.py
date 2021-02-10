import pytest
from api_communication.api_handler import get_downloaded_model
from mock import patch
from requests import exceptions

API_ENDPOINT_URL = "http://test_url"


class MockClass:
    def __init__(self):
        self.content = bytes("mock_model", "utf-8")


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("API_ENDPOINT_URL", API_ENDPOINT_URL)


def side_effect_success(url):
    return MockClass()


def side_effect_failure(url):
    raise exceptions.RequestException("No Model")


def test_getdownloaded_model():
    mock_city = "test_city"

    with patch("requests.get", side_effect=side_effect_success) as exec_api_request:
        assert (exec_api_request.called) is False
        result = get_downloaded_model(mock_city)
        exec_api_request.assert_called_with("{0}/api/cities/{1}/model".format(API_ENDPOINT_URL, mock_city))
        assert result.decode("utf-8") == "mock_model"

    with patch("requests.get", side_effect=side_effect_failure) as exec_api_request:
        assert (exec_api_request.called) is False
        result = get_downloaded_model(mock_city)
        print(result)
        exec_api_request.assert_called_with("{0}/api/cities/{1}/model".format(API_ENDPOINT_URL, mock_city))
        assert result is None
