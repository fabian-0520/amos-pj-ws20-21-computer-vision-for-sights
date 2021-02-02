"""This module contains the views exposed to the user."""
import json
from api.view_handlers import (
    handle_get_trained_city_model,
    handle_persist_sight_image,
    handle_add_new_city,
    handle_get_supported_cities,
    HTTP_200_MESSAGE,
    handle_get_latest_city_model_version,
)
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.request import Request


@api_view(["GET"])
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
    response = handle_get_trained_city_model(city)
    return HttpResponse(response[0], status=response[1])


@api_view(["GET"])
def get_latest_city_model_version(request: Request, city: str) -> HttpResponse:
    """Returns the latest version of the persisted city model.

    Parameters
    ----------
    request: Request
        Request object.
    city: str
        Name of the city.

    Returns
    -------
    response: HttpResponse
        Response object containing the latest model version.
    """
    response = handle_get_latest_city_model_version(city)
    return HttpResponse(response[0], status=response[1])


@api_view(["POST"])
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
    image = request.FILES["image"] if "image" in request.FILES else None
    labels = request.FILES["labels"].read().decode("utf-8") if "labels" in request.FILES else None

    response = handle_persist_sight_image(city, image, labels)
    return HttpResponse(response[0], status=response[1])


@api_view(["POST"])
def add_new_city(request: Request, city: str) -> HttpResponse:
    """Adds a new city to the internally managed list of supported cities.

    Parameters
    ----------
    request: Request
        Request object.
    city: str
        Name of the city to add.

    Returns
    -------
    response: HttpResponse
        Response object containing a default 200 HTTP message.
    """
    response = handle_add_new_city(city)
    return HttpResponse(response[0], status=response[1])


@api_view(["GET"])
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
    response_content = handle_get_supported_cities()
    return HttpResponse(response_content[0], status=response_content[1])


@api_view(["GET"])
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
