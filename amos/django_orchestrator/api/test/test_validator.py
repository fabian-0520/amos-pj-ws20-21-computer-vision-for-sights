"""This module contains the tests for the validator module of the api sub-app."""
from api.validator import is_valid_image_upload, is_city_existing, _is_valid_image_file, _is_valid_labels_file
from copy import copy
from mock import patch
import pytest


def test_is_valid_image_upload(in_memory_uploaded_file_mock, labels_mock):
    with patch('api.validator.is_city_existing', return_value=True), \
         patch('api.validator._is_valid_image_file', return_value=True):
        assert is_valid_image_upload(city='Berlin', image=in_memory_uploaded_file_mock, labels=labels_mock) is True


@pytest.mark.parametrize('city', ['berlin', 'tokyo', 'shanghai'])
def test_is_city_existing(in_memory_uploaded_file_mock, labels_mock, city):
    with patch('api.validator.exec_dql_query', return_value=[[city]]):
        assert is_city_existing(city) is True


def test_is_faulty_image_file():
    assert _is_valid_image_file('I am not an image file!') is False


def test_is_invalid_labels_file(labels_mock):
    labels_copy = copy(labels_mock)
    labels_copy = labels_copy[0:16] + labels_copy[64:]
    assert _is_valid_labels_file(labels_copy) is False
