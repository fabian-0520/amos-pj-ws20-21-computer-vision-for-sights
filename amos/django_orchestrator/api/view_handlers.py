"""This module contains the handling logic behind the available API views."""
from api.validator import is_valid_city, is_valid_image_upload, is_city_existing
from data_django.exec_sql import exec_dql_query
from data_django.handler import get_downloaded_model, upload_image, upload_image_labels, get_latest_model_version
from django.core.files.uploadedfile import InMemoryUploadedFile
from json import dumps
from typing import Union, Tuple
from paramiko import SSHClient, AutoAddPolicy
import os

HTTP_400_MESSAGE = "Wrong request format - please refer to /api/swagger!"
HTTP_200_MESSAGE = "Request successfully executed."


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
    if not is_city_existing(city):
        # TODO: trigger IC component
        pass

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


def handle_trigger_image_crawler(city: str):
    """Returns a list containing the currently supported cities.

    Returns
    -------
    content: str
        Response content.
    http_status: int
        HTTP status code.
    """

    client = SSHClient()
    crawler_user = os.getenv("AWS_USER")
    crawler_host = os.getenv("CRAWLER_HOST")
    registry_host = os.getenv("REGISTRY_HOST")
    pg_host = os.getenv("PG_HOST")
    pg_database = os.getenv("PG_DATABASE")
    pg_user = os.getenv("PG_USER")
    pg_port = os.getenv("PG_PORT")
    pg_password = os.getenv("PG_PASSWORD")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_maps_key = os.getenv("GOOGLE_MAPS_KEY")
    key_filename = "./ec2key.pem"

    print(
        crawler_user,
        crawler_host,
        registry_host,
        pg_host,
        pg_database,
        pg_user,
        pg_port,
        pg_password,
        google_api_key,
        google_maps_key,
    )

    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(crawler_host, username=crawler_user, key_filename=key_filename)
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command(
        "aws ecr get-login-password --region eu-central-1 | docker login"
        " --username AWS --password-stdin {0}".format(registry_host)
    )
    print(ssh_stderr.read())
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("docker pull {0}/crawler:latest".format(registry_host))
    client.exec_command("touch test")
    print(ssh_stderr.read())
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command(
        "docker run -e PGHOST={0} -e PGDATABASE={1} -e PGPORT={2} -e PGUSER={3} -e PGPASSWORD={4}"
        " -e apikey={5}"
        " -e maps_key={6}"
        " {7}/crawler:latest {8}".format(
            pg_host, pg_database, pg_port, pg_user, pg_password, google_api_key, google_maps_key, registry_host, city
        )
    )
    print(ssh_stderr.read())

    client.close()
    return 200
