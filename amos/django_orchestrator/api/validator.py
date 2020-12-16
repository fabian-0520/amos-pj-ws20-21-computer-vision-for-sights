"""This module contains various validation functions for passed
user input like uploaded files or bounding box labels."""
from data_django.exec_sql import exec_dql_query
from django.core.files.uploadedfile import InMemoryUploadedFile
from json import JSONDecodeError, loads


def is_valid_image_upload(city: str, image: InMemoryUploadedFile, labels: str) -> bool:
    """Returns whether the passed request is a valid image upload request.

    Parameters
    ----------
    city: str
        City name.
    image: InMemoryUploadedFile
        Read image.
    labels: str
        Read bounding box labels.

    Returns
    -------
    is_valid_image_upload: bool
        Whether the request is valid for uploading a city image.
    """
    return bool(is_valid_city(city) and _is_valid_image_file(image) and _is_valid_labels_file(labels))


def is_valid_city(city: str, must_be_supported: bool = False) -> bool:
    """Returns whether the passed city name is valid.

    Parameters
    ----------
    city: str
        Name of the requested city.

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
    cities_query = "SELECT DISTINCT(city_name) AS city_name FROM integration_layer.dim_sights_cities"
    cities = set(map(lambda _city: _city[0].upper(), exec_dql_query(cities_query, return_result=True)))
    return city.upper().replace("-", " ") in cities


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
    if image is not None and hasattr(image, "content_type"):
        image_content_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/bmp",
            "image/svg+xml",
            "image/tiff",
            "image/webp",
        ]

        return image.content_type in image_content_types

    return False


def _is_valid_labels_file(labels: str) -> bool:
    """Returns whether the uploaded labels file is valid.

    Parameters
    ----------
    labels: str
        Uploaded labels file as a string.

    Returns
    -------
    is_valid_labels_file: bool
        Whether the uploaded labels file is valid.
    """
    try:
        labels_dict = loads(labels)
        if "boundingBoxes" in labels_dict:
            return all(
                map(lambda bounding_box: _is_valid_bounding_box_label(bounding_box), labels_dict["boundingBoxes"])
            )
    except JSONDecodeError:
        pass

    return False


def _is_valid_bounding_box_label(bounding_box_dict: dict) -> bool:
    """Returns whether the passed dictionary contains a valid bounding box label.

    Parameters
    ----------
    bounding_box_dict: dict
        Bounding box label.

    Returns
    -------
    is_valid_bounding_box_label: bool
        Whether the bounding box label is valid.
    """
    coord_keys = ["ulx", "uly", "lrx", "lry"]

    check_buffer = []
    for key in bounding_box_dict.keys():
        check_buffer.append(key in coord_keys + ["sightName"])
        if key in coord_keys:
            check_buffer.append(isinstance(bounding_box_dict[key], float) and 0.0 <= bounding_box_dict[key] <= 1.0)

    return all(check_buffer)
