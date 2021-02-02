"""This module contains the handling logic behind the available API views."""
from api.validator import is_valid_city, is_valid_image_upload, is_city_existing
from data_django.exec_sql import exec_dql_query
from data_django.handler import get_downloaded_model, upload_image, upload_image_labels, get_latest_model_version
from django.core.files.uploadedfile import InMemoryUploadedFile
from json import dumps
from typing import Union, Tuple
import paramiko
import os

HTTP_400_MESSAGE = "Wrong request format - please refer to /api/swagger!"
HTTP_200_MESSAGE = "Request successfully executed."
CRAWLER_TRIGGERED_FOR_CITIES = []


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
    else:
        return -1, 200


def handle_persist_sight_image(city: str, image: InMemoryUploadedFile, labels: str) -> Tuple[str, int]:
    """Persists a labelled image of a given supported city in the data warehouse.

    Parameters
    ----------
    city: str
        Name of the city.
    image: InMemoryUploadedFile
        Uploaded image.
    labels: str
        Labels string.

    Returns
    -------
    content: str
        Response content.
    http_status: int
        HTTP status code.
    """
    if is_valid_image_upload(city, image, labels):
        source_hash = upload_image(image, city)
        upload_image_labels(labels, source_hash)
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
    if not is_city_existing(city) and city not in CRAWLER_TRIGGERED_FOR_CITIES:
        CRAWLER_TRIGGERED_FOR_CITIES.append(city)  # avoids triggering the crawler multiple times for a single city
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=os.getenv("IC_URL"),
                           username='ubuntu',
                           pkey=paramiko.RSAKey.from_private_key_file('../ec2key.pem'))
        ssh_client.exec_command(_get_crawler_docker_run_command(city))
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
    cities_query = (
        "SELECT DISTINCT(city_name) AS city_name " "FROM integration_layer.dim_sights_cities " "ORDER BY city_name ASC"
    )
    cities = exec_dql_query(cities_query, return_result=True)
    cities = [] if not cities else list(map(lambda _city: _city[0], cities))

    return dumps({"cities": cities}), 200


def _get_crawler_docker_run_command(city: str) -> str:
    return 'docker run -d ' \
           f'-e PGHOST={os.getenv("PGHOST")} ' \
           f'-e PGDATABASE={os.getenv("PGDATABASE")} ' \
           f'-e PGUSER={os.getenv("PGUSER")} ' \
           f'-e PGPORT={os.getenv("PGPORT")} ' \
           f'-e PGPASSWORD={os.getenv("PGPASSWORD")} ' \
           f'-e MAPS_KEY={os.getenv("MAPS_KEY")} ' \
           f'-it crawler {city} ' \
           f'--sights_limit={os.getenv("MAX_SIGHTS_PER_CITY").replace(" ", "%20")} ' \
           f'--limit={os.getenv("MAX_IMAGES_PER_SIGHT")}'
