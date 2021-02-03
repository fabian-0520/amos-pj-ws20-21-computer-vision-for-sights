"""This module contains helper functions for the main app module."""
import os
from time import sleep
from PyQt5.QtWidgets import QComboBox
from api_communication.api_handler import get_supported_cities


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


def update_dropdown(Box_Stadt: QComboBox) -> None:
    while True:
        sleep(30)
        Box_Stadt.clear()
        Box_Stadt.addItems(['Choose City'] + get_supported_cities())
        Box_Stadt.update()
