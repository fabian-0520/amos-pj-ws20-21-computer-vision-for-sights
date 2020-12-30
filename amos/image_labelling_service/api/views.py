"""This module contains the views exposed to the outside world."""
from django.http import HttpResponse
from labelling.new_city_handler import persist_google_vision_labels, LOG_FILE_NAME
from rest_framework.decorators import api_view
from rest_framework.request import Request
import os

HTTP_200_MESSAGE = 'Request successfully executed.'


@api_view(['POST'])
def add_labels_to_existing_city(request: Request, city: str) -> HttpResponse:
    """Retrieves and persists image bounding box labels for an existing city with
    persisted image labels yet into the data warehouse.

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
    return HttpResponse(f'[{city}, EXISTING] {HTTP_200_MESSAGE}', status=200)


@api_view(['POST'])
def add_labels_to_new_city(request: Request, city: str) -> HttpResponse:
    """Retrieves and persists image bounding box labels for a new city without
    any image labels yet into the data warehouse.

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
    persist_google_vision_labels(city)
    return HttpResponse(f'[{city}, NEW] {HTTP_200_MESSAGE}', status=200)


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

    Notes
    -----
    This endpoint is only provided as a best practice.
    """
    return HttpResponse(HTTP_200_MESSAGE, 200)


@api_view(['GET'])
def get_logs(request):
    """Returns the image labelling service logs.

    Parameters
    ----------
    request: Request
        Request object.

    Returns
    -------
    response: HttpResponse
        Response object containing the logs so far.

    Notes
    -----
    This endpoint is provided for monitoring purposes.
    """
    logs = 'None so far'
    if os.path.exists(LOG_FILE_NAME):
        with open(LOG_FILE_NAME, 'r') as file:
            logs = file.read()

    return HttpResponse('LOGS:\n' + logs, 200)
