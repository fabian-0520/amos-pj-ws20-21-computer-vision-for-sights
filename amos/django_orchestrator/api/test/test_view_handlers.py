"""This module contains the tests for the view_handler module of the api sub-app."""
import os
from mock import patch
import pytest
from api.view_handlers import handle_get_trained_city_model, handle_persist_sight_image, \
    handle_get_supported_cities, handle_get_latest_city_model_version, _get_crawler_docker_run_command, \
    CITY_REQUEST_LOGGING_FILE_NAME, _add_city_requested_to_logs, MIN_CITY_REQUESTS_NEEDED_UNTIL_CRAWLING_TRIGGERED, \
    _is_crawling_needed

MODULE_PATH = 'api.view_handlers'


def _erase_city_logging_file():
    try:
        os.remove(CITY_REQUEST_LOGGING_FILE_NAME)
    except OSError:
        pass


@pytest.mark.parametrize('city, is_valid', [('berlin', True), ('tokyo', False)])
def test_handle_get_trained_city_model(city, is_valid):
    with patch(f'{MODULE_PATH}.is_valid_city', return_value=is_valid), \
         patch('api.view_handlers.get_downloaded_model', return_value='<SOME AWESOME .pt MODEL!>'):
        _, status = handle_get_trained_city_model(city)

        assert status == 200 if is_valid else 400


@pytest.mark.parametrize('city, is_valid', [('berlin', True), ('tokyo', False)])
def test_handle_get_latest_city_model_version(city, is_valid):
    with patch(f'{MODULE_PATH}.is_valid_city', return_value=is_valid), \
         patch(f'{MODULE_PATH}.get_latest_model_version', return_value=1):
        version, _ = handle_get_latest_city_model_version(city)

        assert version == 1 if is_valid else -1


def test_handle_persist_sight_image_valid(in_memory_uploaded_file_mock):
    with patch(f'{MODULE_PATH}.upload_image', return_value='dasoij3oi423ifwe234'), \
         patch('api.validator._is_valid_image_file', return_value=True):
        _, status = handle_persist_sight_image('berlin', in_memory_uploaded_file_mock)
        assert status == 200


def test_handle_get_supported_cities():
    with patch(f'{MODULE_PATH}.exec_dql_query', return_value=[['berlin'], ['tokyo']]):
        content, _ = handle_get_supported_cities()
        assert content == '{"cities": ["berlin", "tokyo"]}'


def test_get_crawler_docker_run_command():
    docker_run_command = _get_crawler_docker_run_command('shanghai')
    assert docker_run_command.replace('\n', '') == 'sudo docker run -d -e PGHOST=test -e PGDATABASE=test ' \
                                                   '-e PGUSER=test -e PGPORT=test -e PGPASSWORD=test ' \
                                                   '-e MAPS_KEY=test_key -it crawler shanghai ' \
                                                   '--sights_limit=test_max_sights --limit=test_max_images'


def test_add_city_requested_to_logs():
    _erase_city_logging_file()
    _add_city_requested_to_logs('Kyoto')
    _add_city_requested_to_logs('Kyoto')
    _add_city_requested_to_logs('Guangzhou')

    assert os.path.exists(CITY_REQUEST_LOGGING_FILE_NAME)  # file created
    with open(CITY_REQUEST_LOGGING_FILE_NAME , 'r') as file:
        assert file.read() == 'Kyoto;2\nGuangzhou;1\n'  # expected contents saved

    _erase_city_logging_file()  # cleanup


def test_is_crawling_needed():
    city_of_choice = 'CapitalCity'
    _erase_city_logging_file()

    for _ in range(MIN_CITY_REQUESTS_NEEDED_UNTIL_CRAWLING_TRIGGERED - 1):
        _add_city_requested_to_logs(city_of_choice)  # one too few

    assert _is_crawling_needed(city_of_choice) is False
    _add_city_requested_to_logs(city_of_choice)
    assert _is_crawling_needed(city_of_choice) is True
    _erase_city_logging_file()  # cleanup
