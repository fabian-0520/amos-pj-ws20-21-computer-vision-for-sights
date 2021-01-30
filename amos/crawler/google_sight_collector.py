import googlemaps
from dotenv import load_dotenv

load_dotenv()


def get_sights(region):
    sight_list = []
    search_query = 'sights ' + str(region)

    places_api_key = os.environ.get("places_api_key")
    gmaps = googlemaps.Client(key=places_api_key)
    #Check if api key exist
    if not places_api_key:
        print("Error: no api key")
        return[]
    
    #google places request
    places_response = gmaps.places(search_query)
    places_results = places_response['results']
    if places_results:
        for i in range(len(places_results)):
            sight_name = places_results[i]['name']
            sight_list.append(sight_name)
        print(sight_list)

    else:
        print("Error: something went wrong with maps api")
    return sight_list