"""This module contains the tests for the view_handler module of the api sub-app."""
from mock import patch
import pytest
from api.view_handlers import handle_get_trained_city_model, handle_persist_sight_image, \
    handle_get_supported_cities, handle_get_latest_city_model_version, _get_crawler_docker_run_command


@pytest.mark.parametrize('city, is_valid', [('berlin', True), ('tokyo', False)])
def test_handle_get_trained_city_model(city, is_valid):
    with patch('api.view_handlers.is_valid_city', return_value=is_valid), \
         patch('api.view_handlers.get_downloaded_model', return_value='<SOME AWESOME .pt MODEL!>'):
        _, status = handle_get_trained_city_model(city)

        assert status == 200 if is_valid else 400


@pytest.mark.parametrize('city, is_valid', [('berlin', True), ('tokyo', False)])
def test_handle_get_latest_city_model_version(city, is_valid):
    with patch('api.view_handlers.is_valid_city', return_value=is_valid), \
         patch('api.view_handlers.get_latest_model_version', return_value=1):
        version, _ = handle_get_latest_city_model_version(city)

        assert version == 1 if is_valid else -1


def test_handle_persist_sight_image_valid(in_memory_uploaded_file_mock):
    with patch('api.view_handlers.upload_image', return_value='dasoij3oi423ifwe234'), \
         patch('api.validator._is_valid_image_file', return_value=True):
        _, status = handle_persist_sight_image('berlin', in_memory_uploaded_file_mock)
        assert status == 200


def test_handle_get_supported_cities():
    with patch('api.view_handlers.exec_dql_query', return_value=[['berlin'], ['tokyo']]):
        content, _ = handle_get_supported_cities()
        assert content == '{"cities": ["berlin", "tokyo"]}'


def test_get_crawler_docker_run_command():
    docker_run_command = _get_crawler_docker_run_command('shanghai')
    assert docker_run_command.replace('\n', '') == 'sudo docker run -d -e PGHOST=test -e PGDATABASE=test ' \
                                                   '-e PGUSER=test -e PGPORT=test -e PGPASSWORD=test ' \
                                                   '-e MAPS_KEY=test_key -it crawler shanghai ' \
                                                   '--sights_limit=test_max_sights --limit=test_max_images'
