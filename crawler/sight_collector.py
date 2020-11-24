import os

import requests
from dotenv import load_dotenv

load_dotenv()


def get_sights(lat, lng):
    base_url = "https://api.opentripmap.com/0.1/en/places/radius"
    apikey = os.environ.get("apikey")
    payload = {"lang": "en", "lat": lat, "lon": lng, "limit": 100, "radius": 10000, "apikey": apikey, "rate": "3h"}
    sights_response = requests.get(base_url, payload)
    response_json = sights_response.json()
    sight_list = []
    if "features" in response_json:
        for sight in response_json["features"]:
            sight_list.append(sight["properties"]["name"])
    return sight_list
