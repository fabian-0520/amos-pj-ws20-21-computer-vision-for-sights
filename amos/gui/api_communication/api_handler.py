"""This module contains necessary business logic in order to communicate with the dwh_communication warehouse."""
from typing import Optional
import requests
import os

os.environ["API_ENDPOINT_URL"] = "http://ec2-35-158-44-78.eu-central-1.compute.amazonaws.com:8002"
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
    api_endpoint_url = os.environ["API_ENDPOINT_URL"]
    print("{0}/api/cities/{1}/model".format(api_endpoint_url, city.upper()))
    try:

        latest_version = get_dwh_model_version(city)
        r = requests.get("{0}/api/cities/{1}/model".format(api_endpoint_url, city.upper()))

        file = open("weights/versions.txt", "r")
        lines = file.readlines()
        file.close()
        file = open("weights/versions.txt", "w")
        for line in lines:
            if line.split("=")[0].upper() != city.upper():
                file.write(line)
        file.write(city.upper() + "=" + str(latest_version) + "\n")
        file.close()
        return r.content
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_dwh_model_version(city: str) -> int:
    """Returns the current model version in dwh.
    Parameters
    ----------
    city: str
        Name of the city.
    Returns
    -------
    version: int or None
        Retrieved version number.

    """
    api_endpoint_url = os.environ["API_ENDPOINT_URL"]
    print("{0}/api/cities/{1}/model/version".format(api_endpoint_url, city.upper()))
    try:
        r = requests.get("{0}/api/cities/{1}/model/version".format(api_endpoint_url, city.upper()))
        return int(r.text)
    except requests.exceptions.RequestException as e:
        print(e)
        return None
