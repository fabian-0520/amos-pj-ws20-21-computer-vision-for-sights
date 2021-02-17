"""This module contains the handling logic behind the available API views."""
from json import dumps
from multiprocessing import Lock
from typing import Union, Tuple
import os
import paramiko
from django.core.files.uploadedfile import InMemoryUploadedFile
from api.validator import is_valid_city, is_valid_image_upload, is_city_existing
from data_django.exec_sql import exec_dql_query
from data_django.handler import get_downloaded_model, upload_image, get_latest_model_version

CITY_REQUEST_LOGGING_FILE_LOCK = Lock()
CITY_REQUEST_LOGGING_FILE_NAME = 'city_requests.log'
CRAWLER_TRIGGERED_FOR_CITIES = []
HTTP_400_MESSAGE = "Wrong request format - please refer to /api/swagger!"
HTTP_200_MESSAGE = "Request successfully executed."
MIN_CITY_REQUESTS_NEEDED_UNTIL_CRAWLING_TRIGGERED = 100


def handle_get_trained_city_model(city: str) -> Tuple[Union[str, bytes], int]:
    """Returns a trained city model as a .pt file.

    Parameters
    ----------
    city: str
        Name of the city.

    Returns
    -------
    content: str or bytes
        Response content.
    http_status: int
        HTTP status code.
    """
    if is_valid_city(city):
        model = get_downloaded_model(city)
        return model, 200

    return HTTP_400_MESSAGE, 400


def handle_get_latest_city_model_version(city: str) -> Tuple[int, int]:
    """Returns a trained city model as a .pt file.

    Parameters
    ----------
    city: str
        Name of the city.

    Returns
    -------
    content: int
        Response content.
    http_status: int
        HTTP status code.
    """
    if is_valid_city(city):
        version = get_latest_model_version(city)
        return version, 200

    return -1, 200


def handle_persist_sight_image(city: str, image: InMemoryUploadedFile) -> Tuple[str, int]:
    """Persists an image of a given supported city in the data warehouse.

    Parameters
    ----------
    city: str
        Name of the city.
    image: InMemoryUploadedFile
        Uploaded image.

    Returns
    -------
    content: str
        Response content.
    http_status: int
        HTTP status code.
    """
    if is_valid_image_upload(city, image):
        upload_image(image, city)
        return HTTP_200_MESSAGE, 200

    return HTTP_400_MESSAGE, 400


def handle_add_new_city(city: str) -> Tuple[str, int]:
    """Adds a new city to the internally managed list of supported cities.

    Parameters
    ----------
    city: str
        Name of the city to add.

    Returns
    -------
    content: str
        Response content.
    http_status: int
        HTTP status code.
    """
    if not is_city_existing(city):
        _add_city_requested_to_logs(city)

        if _is_crawling_needed(city):
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=os.getenv("IC_URL"),
                               username='ubuntu',
                               pkey=paramiko.RSAKey.from_private_key_file('ec2key.pem'))
            cmd = _get_crawler_docker_run_command(city)
            print(f'Performing: {cmd} on remote image crawler {os.getenv("IC_URL")}')
            _, _, stderr = ssh_client.exec_command(cmd)
            print(f'Received error (if any): {stderr.readlines()}')
            ssh_client.close()

    return HTTP_200_MESSAGE, 200


def handle_get_supported_cities() -> Tuple[str, int]:
    """Returns a list containing the currently supported cities.

    Returns
    -------
    content: str
        Response content.
    http_status: int
        HTTP status code.
    """
    cities_query = 'select distinct(city_name) from data_mart_layer.current_trained_models order by city_name asc'
    cities = exec_dql_query(cities_query, return_result=True)
    cities = [] if not cities else list(map(lambda _city: _city[0], cities))

    return dumps({'cities': cities}), 200


def _add_city_requested_to_logs(requested_city: str) -> None:
    """Persists the information that a given city has been requested in a logging file
    for later data stewardship.

    Parameters
    ----------
    requested_city: str
        Requested city name.
    """
    with CITY_REQUEST_LOGGING_FILE_LOCK:
        _create_city_logging_file_if_not_exists()
        new_content = _get_new_city_logging_file_content(requested_city)
        with open(CITY_REQUEST_LOGGING_FILE_NAME, 'w') as target_file:
            target_file.write(new_content)


def _create_city_logging_file_if_not_exists():
    """Creates a city logging file if it does not exist."""
    if not os.path.exists(CITY_REQUEST_LOGGING_FILE_NAME):
        with open(CITY_REQUEST_LOGGING_FILE_NAME, 'w'):
            print('New logging file has been created!')


def _get_crawler_docker_run_command(city: str) -> str:
    """Returns the docker run command needed to trigger the crawler.

    Parameters
    ----------
    city: str
        City to crawl sights for.

    Returns
    -------
    run_command: str
        Docker run command for the crawler.
    """
    return 'sudo docker run -d ' \
           f'-e PGHOST={os.getenv("PGHOST")} ' \
           f'-e PGDATABASE={os.getenv("PGDATABASE")} ' \
           f'-e PGUSER={os.getenv("PGUSER")} ' \
           f'-e PGPORT={os.getenv("PGPORT")} ' \
           f'-e PGPASSWORD={os.getenv("PGPASSWORD")} ' \
           f'-e MAPS_KEY={os.getenv("MAPS_KEY")} ' \
           f'-it crawler {city} ' \
           f'--sights_limit={os.getenv("MAX_SIGHTS_PER_CITY")} ' \
           f'--limit={os.getenv("MAX_IMAGES_PER_SIGHT")}'


def _get_new_city_logging_file_content(requested_city: str) -> str:
    """Returns the new content of the city logging file based on the received requested city.

    Parameters
    ----------
    requested_city: str
        City whose support has just been requested.

    Returns
    -------
    new_content: str
        New content for the file.
    """
    new_city_content, city_already_requested = '', False

    with open(CITY_REQUEST_LOGGING_FILE_NAME, 'r') as old_file:
        for line in old_file.readlines():
            contents = line.split(';')
            line_city, line_counter = contents[0], int(contents[1])
            if line_city == requested_city:  # simply copy content
                city_already_requested = True
                line_counter += 1

            new_city_content += f'{line_city};{line_counter}\n'

    if not city_already_requested:
        new_city_content += f'{requested_city};{1}\n'

    return new_city_content


def _is_crawling_needed(requested_city: str) -> bool:
    """Returns whether the image crawler should be triggered.

    Parameters
    ----------
    requested_city: str
        Requested city.

    Returns
    -------
    is_crawling_needed: bool
        Whether the crawler should be triggered.
    """
    with CITY_REQUEST_LOGGING_FILE_LOCK:
        with open(CITY_REQUEST_LOGGING_FILE_NAME, 'r') as old_file:
            for line in old_file.readlines():
                contents = line.split(';')
                line_city, count = contents[0], int(contents[1])
                if line_city == requested_city and count >= MIN_CITY_REQUESTS_NEEDED_UNTIL_CRAWLING_TRIGGERED:
                    return True

    return False
