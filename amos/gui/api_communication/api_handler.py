"""This module contains necessary business logic in order to communicate with the dwh_communication warehouse."""
from typing import Optional, List
import requests
import os
import json

os.environ["API_ENDPOINT_URL"] = "http://ec2-18-159-48-86.eu-central-1.compute.amazonaws.com:8002"
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
    print("{0}/api/cities/{1}/model/version".format(api_endpoint_url, city))
    try:
        r = requests.get("{0}/api/cities/{1}/model/version".format(api_endpoint_url, city))
        return int(r.text)
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def send_city_request(city: str) -> None:
    """Sends city request to trigger training for new city.

    Parameters
    ----------
    city: str
        Name of the city.

    Returns
    -------
    None

    """
    api_endpoint_url = os.environ["API_ENDPOINT_URL"]
    try:
        requests.post("{0}/api/cities/{1}/add".format(api_endpoint_url, city.upper()))
        return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_supported_cities() -> List[str]:
    """Retrieves the supported city names.

    Returns
    -------
    city_list: list[str]
        List of supported cities (alphabetically ordered).
    """
    api_endpoint_url = os.environ["API_ENDPOINT_URL"]
    print("{0}/api/cities".format(api_endpoint_url))
    try:
        r = requests.get("{0}/api/cities".format(api_endpoint_url))
        cities = json.loads(r.text)
        return list(
            map(
                lambda city: city.replace('_', ' ').title(),
                sorted(cities['cities'])
            )
        )
    except requests.exceptions.RequestException as e:
        print(e)
        return []

