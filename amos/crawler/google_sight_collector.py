import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()


def get_sights(region):
    sight_list = []
    search_query = 'sights ' + str(region)

    maps_key = os.environ.get("MAPS_KEY")
    gmaps = googlemaps.Client(key=maps_key)
    #Check if api key exist
    if not maps_key:
        print("Error: no api key")
        return[]
    
    #google places request
    places_response = gmaps.places(search_query)
    places_results = places_response['results']
    if places_results:
        for i in range(len(places_results)):
            sight_name = places_results[i]['name']
            sight_list.append(sight_name)

    else:
        print("Error: something went wrong with maps api")
    return sight_list