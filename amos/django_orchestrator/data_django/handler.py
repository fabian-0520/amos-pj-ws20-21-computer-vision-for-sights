"""This module contains necessary business logic in order to communicate with the data warehouse."""
from hashlib import md5
from typing import Optional
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from psycopg2 import Binary
from data_django.exec_sql import exec_dql_query, exec_dml_query


def upload_image(image: InMemoryUploadedFile, city: str) -> str:
    """Uploads an image for the specified city and returns the respective lookup hash.

    Parameters
    ----------
    image: InMemoryUploadedFile
        Image to insert.
    city: str
        City the image belongs to.

    Returns
    -------
    source_hash: str
        Image lookup hash.
    """
    empty_dml_query = (
        "INSERT INTO load_layer.sight_images(sight_image, sight_city, "
        "sight_image_height, sight_image_width, sight_image_data_source) "
        "VALUES (%s, %s, %s, %s, %s)"
    )

    img = Image.open(image)
    img_bytes = img.tobytes()
    source_hash = md5(img_bytes).hexdigest()  # hash image to guarantee unique user input to DWH
    width = img.size[0]
    height = img.size[1]

    query_filling_params = (Binary(img_bytes), city, height, width, source_hash)
    exec_dml_query(empty_dml_query, query_filling_params)

    return source_hash


def get_downloaded_model(city: str) -> Optional[bytes]:
    """Returns the downloaded and trained model for the specified city if it is available in the data warehouse.

    Parameters
    ----------
    city: str
        Name of the city.

    Returns
    -------
    found_model: bytes or None
        Retrieved .pt model file.
    """
    trained_model_query = (
        f"SELECT trained_model FROM data_mart_layer.current_trained_models " f"WHERE city_name = '{city.upper()}'"
    )
    found_model = exec_dql_query(trained_model_query, return_result=True)
    if found_model:
        return found_model[0][0].tobytes()

    return None


def get_latest_model_version(city: str) -> int:
    """Returns the version number of the latest model belonging to the passed city.

    Parameters
    ----------
    city: str
        Name of the city.

    Returns
    -------
    latest_version: int
        Latest model version.
    """
    trained_model_query = (
        f"SELECT version FROM data_mart_layer.current_trained_models " f"WHERE city_name = '{city.upper()}'"
    )
    found_version = exec_dql_query(trained_model_query, return_result=True)
    if found_version:
        return int(found_version[0][0])

    return -1
