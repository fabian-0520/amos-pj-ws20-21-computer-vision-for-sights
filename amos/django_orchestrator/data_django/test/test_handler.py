"""This module contains the tests for the handler module of the data sub-app."""
from data_django.handler import upload_image, upload_image_labels, _get_image_label_dml_query, get_downloaded_model, \
    get_latest_model_version
from mock import patch, PropertyMock


def test_upload_image(in_memory_uploaded_file_mock, md5_mock):
    with patch("data_django.handler.Image", new_callable=PropertyMock, return_value=in_memory_uploaded_file_mock), \
         patch("data_django.handler.md5", return_value=md5_mock), \
         patch("data_django.handler.exec_dml_query"):
        assert upload_image(in_memory_uploaded_file_mock, "Berlin") == md5_mock.hexdigest()


def test_upload_image_labels(labels_mock, md5_mock):
    with patch("data_django.handler.exec_dml_query") as exec_mock:
        upload_image_labels(labels_mock, md5_mock.hexdigest())
        assert exec_mock.called
        called_query = exec_mock.mock_calls[0][1][0]
        assert str(md5_mock.hexdigest()) in called_query


def test_get_image_label_dml_query(labels_mock, md5_mock):
    built_query = _get_image_label_dml_query(labels_mock, md5_mock.hexdigest())
    assert (
        built_query == "INSERT INTO load_layer.sight_image_labels(sight_image_data_source, sight_labels) "
        "VALUES ('b'testtesttesttesttesttesttest'', "
        "'{\""
        '(0.12122,0.34212,0.33311,0.12315,Brandenburger Tor)",'
        '"(0.12122,0.34212,0.33311,0.12315,Siegessaeule)'
        "\"}')"
    )


def test_get_downloaded_model_found(model_mock):
    with patch("data_django.handler.exec_dql_query", return_value=[[model_mock]]):
        result_model = get_downloaded_model("berlin")
        assert result_model == model_mock.tobytes()


def test_get_downloaded_model_not_found():
    with patch("data_django.handler.exec_dql_query", return_value=[]):
        result_model = get_downloaded_model("berlin")
        assert result_model is None


def test_get_latest_model_version():
    with patch("data_django.handler.exec_dql_query", return_value=[['22']]):
        result_model = get_latest_model_version("berlin")
        assert result_model == 22


def test_get_latest_model_version_not_found():
    with patch("data_django.handler.exec_dql_query", return_value=[]):
        result_model = get_latest_model_version("berlin")
        assert result_model == -1
