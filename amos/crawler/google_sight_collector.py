import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()


def get_sights(region, max_sights):
    sight_list = []
    search_query = "sights " + str(region)

    maps_key = os.environ.get("MAPS_KEY")
    gmaps = googlemaps.Client(key=maps_key)
    # Check if api key exist
    if not maps_key:
        print("Error: no api key")
        return []

    # google places request
    places_response_german = gmaps.places(search_query, language="de")
    places_response_english = gmaps.places(search_query)

    sight_list = get_sights_from_json(places_response_german) + get_sights_from_json(places_response_english)
    sight_list = list(dict.fromkeys(sight_list))
    print(sight_list)

    return sight_list[:max_sights]


def get_sights_from_json(places_response: dict):
    sight_list = []
    places_results = places_response["results"]
    if places_results:
        for i in range(len(places_results)):
            sight_name = places_results[i]["name"]
            sight_list.append(sight_name)
    else:
        print("Error: something went wrong with maps api")
    return sight_list
