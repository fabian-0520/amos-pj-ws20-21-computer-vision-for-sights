"""This module contains the handling logic behind the available API views."""
from api.validator import is_valid_city, is_valid_image_upload, is_city_existing
from data.exec_sql import exec_dql_query
from data.handler import get_downloaded_model, upload_image, upload_image_labels
from django.core.files.uploadedfile import InMemoryUploadedFile
from json import dumps
from typing import Union, Tuple

HTTP_400_MESSAGE = 'Wrong request format - please refer to /api/swagger!'
HTTP_200_MESSAGE = 'Request successfully executed.'


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
    cities_query = 'SELECT DISTINCT(city_name) AS city_name ' \
                   'FROM integration_layer.dim_sights_cities ' \
                   'ORDER BY city_name ASC'
    cities = exec_dql_query(cities_query, return_result=True)

    cities = [] if not cities else list(map(lambda _city: _city[0], cities))

    return dumps({'cities': cities}), 200
