"""This module contains various validation functions for passed user inputs like uploaded files."""
import imghdr
from django.core.files.uploadedfile import InMemoryUploadedFile
from data_django.exec_sql import exec_dql_query


def is_valid_image_upload(city: str, image: InMemoryUploadedFile) -> bool:
    """Returns whether the passed request is a valid image upload request.

    Parameters
    ----------
    city: str
        City name.
    image: InMemoryUploadedFile
        Read image.

    Returns
    -------
    is_valid_image_upload: bool
        Whether the request is valid for uploading a city image.
    """
    return bool(is_valid_city(city) and _is_valid_image_file(image))


def is_valid_city(city: str, must_be_supported: bool = False) -> bool:
    """Returns whether the passed city name is valid.

    Parameters
    ----------
    city: str
        Name of the requested city.
    must_be_supported: bool
        Whether the city must be already supported.

    Returns
    -------
    is_valid: bool
        Whether the city is valid.
    """
    return bool(
        city is not None
        and isinstance(city, str)
        and len(city) > 3
        and ((must_be_supported and is_city_existing(city)) or not must_be_supported)
    )


def is_city_existing(city: str) -> bool:
    """Returns whether the passed city exists.

    Parameters
    ----------
    city: str
        Name of the city.

    Returns
    -------
    is_existing: bool
        Whether the passed city exists.
    """
    cities_query = "select distinct(city_name) from data_mart_layer.current_trained_models"
    cities = set(map(lambda _city: _city[0].upper(), exec_dql_query(cities_query, return_result=True)))
    return city.upper() in cities


def _is_valid_image_file(image: InMemoryUploadedFile) -> bool:
    """Returns whether the passed file is a valid image file.

    Parameters
    ----------
    image: InMemoryUploadedFile
        Uploaded image file.

    Returns
    -------
    is_valid: bool
        Whether the uploaded image file is valid.
    """
    image_content_types = [
        "jpeg",
        "png",
        "gif",
        "bmp",
        "webp",
        "tiff"
    ]

    return imghdr.what(file=image.file) in image_content_types
