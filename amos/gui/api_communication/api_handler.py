"""This module contains necessary business logic in order to communicate with the dwh_communication warehouse."""
from typing import Optional
import requests
from os import environ

HTTP_400_MESSAGE = "Wrong request format - please refer to /api/swagger!"
HTTP_200_MESSAGE = "Request successfully executed."


def get_downloaded_model(city: str) -> Optional[bytes]:
    """Returns the downloaded and trained model for the specified city if it is via api.

    Parameters
    ----------
    city: str
        Name of the city.

    Returns
    -------
    found_model: bytes or None
        Retrieved .pt model file.
    """
    api_endpoint_url = environ["API_ENDPOINT_URL"]
    print("{0}/api/cities/{1}/model".format(api_endpoint_url, city.upper()))
    try:
        r = requests.get("{0}/api/cities/{1}/model".format(api_endpoint_url, city.upper()))
        return r.content
    except requests.exceptions.RequestException as e:
        print(e)
        return None
