import os

import requests
from dotenv import load_dotenv

load_dotenv()


def get_sights(region, sights_limit):
    sight_list = []
    base_url = "https://api.opentripmap.com/0.1/en/places/radius"
    maps_url = "https://maps.googleapis.com/maps/api/geocode/json"

    apikey = os.environ.get("apikey")
    maps_key = os.environ.get("maps_key")
    # Check if api keys exist
    if not apikey or not maps_key:
        print("Error: no api keys")
        return []

    # google maps request
    geocode_payload = {"address": region, "key": maps_key}
    maps_response = requests.get(maps_url, geocode_payload)
    maps_response_json = maps_response.json()
    if maps_response.status_code == 200 and maps_response_json["status"] == "OK":
        print(maps_response_json)
        location = maps_response_json["results"][0]["geometry"]["location"]
        lat = location["lat"]
        lng = location["lng"]

        # start sights list request
        payload = {"lang": "en", "lat": lat, "lon": lng, "limit": sights_limit, "radius": 10000, "apikey": apikey,
                   "rate": "3h"}
        sights_response = requests.get(base_url, payload)
        response_json = sights_response.json()
        if "features" in response_json:
            for sight in response_json["features"]:
                sight_list.append(sight["properties"]["name"])
    else:
        print("Error: something went wrong with maps api")
    return sight_list
