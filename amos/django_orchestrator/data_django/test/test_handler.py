"""This module contains the tests for the handler module of the data sub-app."""
from mock import patch, PropertyMock
from data_django.handler import upload_image, get_downloaded_model, get_latest_model_version

FUNCTION_PATH = "data_django.handler.exec_dql_query"


def test_upload_image(in_memory_uploaded_file_mock, md5_mock):
    with patch("data_django.handler.Image", new_callable=PropertyMock, return_value=in_memory_uploaded_file_mock), \
         patch("data_django.handler.md5", return_value=md5_mock), \
         patch("data_django.handler.exec_dml_query"):
        assert upload_image(in_memory_uploaded_file_mock, "Berlin") == md5_mock.hexdigest()


def test_get_downloaded_model_found(model_mock):
    with patch(FUNCTION_PATH, return_value=[[model_mock]]):
        result_model = get_downloaded_model("berlin")
        assert result_model == model_mock.tobytes()


def test_get_downloaded_model_not_found():
    with patch(FUNCTION_PATH, return_value=[]):
        result_model = get_downloaded_model("berlin")
        assert result_model is None


def test_get_latest_model_version():
    with patch(FUNCTION_PATH, return_value=[['22']]):
        result_model = get_latest_model_version("berlin")
        assert result_model == 22


def test_get_latest_model_version_not_found():
    with patch(FUNCTION_PATH, return_value=[]):
        result_model = get_latest_model_version("berlin")
        assert result_model == -1
