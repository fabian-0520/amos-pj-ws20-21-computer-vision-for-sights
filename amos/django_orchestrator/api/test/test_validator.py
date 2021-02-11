"""This module contains the tests for the validator module of the api sub-app."""
from mock import patch
import pytest
from api.validator import is_valid_image_upload, is_city_existing, _is_valid_image_file
from conftest import ImageMock


def test_is_valid_image_upload(in_memory_uploaded_file_mock):
    with patch('api.validator.is_city_existing', return_value=True), \
         patch('api.validator._is_valid_image_file', return_value=True):
        assert is_valid_image_upload(city='Berlin', image=in_memory_uploaded_file_mock) is True


@pytest.mark.parametrize('city', ['berlin', 'tokyo', 'shanghai'])
def test_is_city_existing(city):
    with patch('api.validator.exec_dql_query', return_value=[[city]]):
        assert is_city_existing(city) is True


def test_is_faulty_image_file(image_mock: ImageMock) -> None:
    with pytest.raises(AttributeError):
        _is_valid_image_file(image_mock)
