from api.handler import get_downloaded_model, upload_image, upload_image_labels
from api.validator import is_valid_image_upload, is_valid_city
from db.exec_sql import exec_dql_query
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.request import Request

HTTP_400_MESSAGE = 'Wrong request format - please refer to /api/swagger!'
HTTP_200_MESSAGE = 'Request successfully executed.'


@api_view(['GET'])
def get_trained_city_model(request: Request, city: str) -> HttpResponse:
    """Returns a trained city model as a .pt file.

    Parameters
    ----------
    request: Request
        Request object.
    city: str
        Name of the city.

    Returns
    -------
    response: HttpResponse
        Response object containing the trained model as a .pt file.
    """
    if is_valid_city(city):
        model = get_downloaded_model(city)
        return HttpResponse(model, status=200)

    return HttpResponse(HTTP_400_MESSAGE, status=400)


@api_view(['POST'])
def persist_sight_image(request: Request, city: str) -> HttpResponse:
    """Persists a labelled image of a given supported city in the data warehouse.

    Parameters
    ----------
    request: Request
        Request object.
    city: str
        Name of the city.

    Returns
    -------
    response: HttpResponse
        Response object containing a status message.
    """
    image = request.FILES['image'] if 'image' in request.FILES else None
    labels = request.FILES['labels'].read().decode('utf-8') if 'labels' in request.FILES else None

    if is_valid_image_upload(city, image, labels):
        source_hash = upload_image(image, city)
        upload_image_labels(labels, source_hash)
        return HttpResponse(HTTP_200_MESSAGE, status=200)

    return HttpResponse(HTTP_400_MESSAGE, status=400)


@api_view(['POST'])
def add_new_city(request: Request) -> HttpResponse:
    """Adds a new city to the internally managed list of supported cities.

    Parameters
    ----------
    request: Request
        Request object.

    Returns
    -------
    response: HttpResponse
        Response object containing a default 200 HTTP message.
    """
    # TODO trigger IC
    return HttpResponse(HTTP_200_MESSAGE, status=200)


@api_view(['GET'])
def get_supported_cities(request: Request) -> HttpResponse:
    """Returns a list containing the currently supported cities.

    Parameters
    ----------
    request: Request
        Request object.

    Returns
    -------
    response: HttpResponse
        Response object containing the list of supported cities.
    """
    cities_query = 'SELECT DISTINCT(city_name) AS city_name ' \
                   'FROM integration_layer.dim_sights_cities ' \
                   'ORDER BY city_name ASC'
    cities = exec_dql_query(cities_query, return_result=True)

    cities = [] if not cities else list(map(lambda _city: _city[0], cities))
    return HttpResponse(cities, status=200)


@api_view(['GET'])
def get_index(request):
    """Returns a default 200 HTTP code.

    Parameters
    ----------
    request: Request
        Request object.

    Returns
    -------
    response: HttpResponse
        Response object containing a default 200 status code.
    """
    return HttpResponse(status=200)
