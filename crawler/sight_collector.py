import requests


def get_sights(lat, lng, apikey):
    base_url = "https://api.opentripmap.com/0.1/en/places/radius"
    payload = {"lat": str(lat), "long": str(lng), "limit": 100, "radius": 10000, "apikey": apikey}
    sights_response = requests.get(base_url, payload)

    response_json = sights_response.json()
    sight_list = []
    for sight in response_json:
        sight_list.append(sight["name"])
    return sight_list
