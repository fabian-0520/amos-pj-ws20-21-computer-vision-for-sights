"""This module contains helper functions for the main app module."""
import os
from time import sleep
from PyQt5.QtWidgets import QComboBox
from api_communication.api_handler import get_supported_cities
from geotext import GeoText as filterString


def wipe_prediction_input_images(images_base_path: str) -> None:
    """Wipes the passed images load directory clean of any existing files.

    Parameters
    ----------
    images_base_path: str
        Directory for input images for prediction.
    """
    # delete images from data
    if os.path.isdir(images_base_path):
        for file in os.listdir(images_base_path):
            os.remove(f'{images_base_path}/{file}')

    # create images directory
    else:
        os.makedirs(images_base_path)


def get_current_prediction_output_path(prediction_output_base_path: str, image_name: str) -> str:
    """Returns the path of the current prediction output images.

    Parameters
    ----------
    prediction_output_base_path: str
        Prediction output base path.
    image_name: str
        Name of the image.

    Returns
    -------
    output_path: str
        Output path in which the predicted images are inserted.
    """
    dirs = [(prediction_output_base_path + d) for d in os.listdir(prediction_output_base_path)]
    newest_dir = max(dirs, key=os.path.getmtime)
    return newest_dir + '/' + image_name.replace('/', '')


def update_dropdown(box_city: QComboBox) -> None:
    while True:
        sleep(30)
        selected = box_city.currentText()
        box_city.clear()
        box_city.addItems(['Choose City'] + initialize_cities())
        box_city.setCurrentText(selected)
        box_city.update()


def filter_city(input_city: str) -> str:
    """Returns the list of filtered cities from input string.

    Parameters
    ----------
    input_city: str
        Input string.

    Returns
    -------
    result: List[str]
        Result of city filtering.
    """
    # input_city = string.capwords(input_city.lower())
    result = filterString(input_city).cities
    return result


def initialize_cities() -> list:
    """Returns a list of all supported cities with which points of interest can be detected. 
    If there is a connection to the DOS, the cities in our DWH are returned.
    Otherwise the locally available cities are returned.
    """
    if get_supported_cities():
        supported_cities = get_supported_cities()
    else:
        supported_cities = []
        for filename in os.listdir('weights'):
            if filename.endswith(".pt"):
                pretty_modelname = filename[:-3].replace("_", " ").title()
                supported_cities.append(pretty_modelname)
    return supported_cities
