"""This module contains the tests for the handler module of the dwh_communication sub-app."""
from dwh_communication.dwh_handler import upload_image_labels, _get_image_label_dml_query
from mock import patch


def test_upload_image_labels(labels_mock, md5_mock):
    with patch("dwh_communication.dwh_handler.exec_dml_query") as exec_mock:
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
