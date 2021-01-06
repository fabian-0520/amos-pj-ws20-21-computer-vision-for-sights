"""This module contains the business logic for reading images, retrieving their labels,

and merging them into the data warehouse - provided the specified city is yet not supported.
"""
from dwh_communication.exec_dwh_sql import exec_dql_query, exec_dml_query
from google.cloud import vision
from google.protobuf.json_format import MessageToDict
from os import environ
from PIL import Image
from typing import Optional, Dict, Union, Tuple, List
import datetime
import io
import pytz
import re

BOUNDING_BOX_DECIMALS_PRECISION = 5  # 5 decimal places for relative bounding box coordinates
LOG_FILE_NAME = 'special_incidents.log'


def persist_google_vision_labels(city_name: str) -> None:
    """Persists bounding box labels for sights of the given city in the data warehouse.

    Parameters
    ----------
    city_name: str
        Name of the city to retrieve bounding box labels for.
    """
    image_ids_for_labelling = _read_image_ids_for_labelling(city_name)
    if isinstance(image_ids_for_labelling, list) and len(image_ids_for_labelling) > 0:
        for image_id in image_ids_for_labelling:
            log_incident(f'Trying to retrieve bounding box labels for image {image_id} '
                         f'[new city: {city_name.upper()}].')
            if _label_image(image_id):
                log_incident(f'Retrieving + persisting bounding box labels for image '
                             f'{image_id} successful [new city: {city_name.upper()}].')
            else:
                log_incident(f'Google vision API has identified no landmark for image {image_id}.')
    else:
        log_incident(f'No images to be labelled found [new city: {city_name.upper()}].')


def _get_image_resolution(image_bytes: bytes) -> Tuple[int, int]:
    """Returns both the width and height of the given image.

    Parameters
    ----------
    image_bytes: bytes
        Image file in raw format.

    Returns
    -------
    width: int
        Image width.
    height: int
        Image height.

    Notes
    -----
    In order to put less load on the data warehouse, the image resolution determination is done in this service
    instead of performing costly joins on the DWH side and retrieving them from there, respectively.

    Both parameters are needed later to compute relative bounding box positions w.r.t. image resolutions.
    """
    image = Image.open(io.BytesIO(image_bytes))
    return image.width, image.height


def _get_landmarks_from_vision(image_bytes: bytes) -> Optional[List[Dict[str, Union[str, float, dict, list]]]]:
    """Retrieves and returns the landmarks for a given image from the Google Vision API.

    Parameters
    ----------
    image_bytes: bytes
         Image file in raw format.

    Returns
    -------
    landmark: dict[str, str or float or dict or list]
        Identified landmarks as a dictionary.

    Notes
    -----
    Since this function directly communicates with the non-mockable Google Vision API, it is not tested.
    However, the functionality of this function has been validated
    through numerous informal integration tests during development.
    """
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    landmark_annotations = MessageToDict(client.landmark_detection(image=image)._pb)

    if 'landmarkAnnotations' in landmark_annotations and len(landmark_annotations['landmarkAnnotations']) > 0:
        landmark_annotations = landmark_annotations['landmarkAnnotations']
    else:
        landmark_annotations = None

    return landmark_annotations


def _get_merged_bounding_box_string(bounding_box_strings: List[str]) -> str:
    """Returns the merged and final bounding boxes string that is compatible with the data warehouse.

    Parameters
    ----------
    bounding_box_strings: list[str]
        List of bounding box strings.

    Returns
    -------
    bounding_box_string: str
        Final, merged bounding boxes string.
    """
    merged_bounding_boxes, n_boxes = '{', len(bounding_box_strings)

    for bounding_box_idx in range(n_boxes):
        merged_bounding_boxes += bounding_box_strings[bounding_box_idx]
        if bounding_box_idx < n_boxes - 1:  # still bounding boxes to come
            merged_bounding_boxes += ','

    merged_bounding_boxes += '}'
    return merged_bounding_boxes


def _label_image(image_id: int) -> bool:
    """Labels the image with the given image ID from the data warehouse and returns if the labelling was successful.

    Parameters
    ----------
    image_id: int
        Image id.

    Returns
    -------
    is_successfully_labelled: bool
        Whether the labelling was successful.
    """
    # query for image
    dql_query = 'SELECT img.image_file AS file, img.image_source AS source ' \
                'FROM integration_layer.dim_sights_images AS img ' \
                f'WHERE img.image_id = {image_id} '
    content = exec_dql_query(dql_query, return_result=True)

    # retrieve bounding boxes in data warehouse-readable format
    image_bytes, image_source = bytes(content[0][0]), content[0][1]
    raw_landmark = _get_landmarks_from_vision(image_bytes)
    is_label_retrieved = raw_landmark is not None

    if is_label_retrieved:
        width, height = _get_image_resolution(image_bytes)
        bounding_box_strings = [_parse_landmark_to_bounding_box_str(landmark_annotation, width, height)
                                for landmark_annotation in raw_landmark]
        final_bounding_boxes_string = _get_merged_bounding_box_string(bounding_box_strings)

        # merge labels into data warehouse
        dml_query = "INSERT INTO load_layer.sight_image_labels(sight_image_data_source, sight_labels) " \
                    f"VALUES ('{image_source}', '{final_bounding_boxes_string}')"
        exec_dml_query(dml_query, filling_parameters=None)

    return is_label_retrieved


def log_incident(msg: str) -> None:
    """Logs special incidents in a logging file.

    Parameters
    ----------
    msg: str
        Logging message.
    """
    with open(LOG_FILE_NAME, 'a+') as file:
        time = datetime.datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
        file.write(f'[{time} UTC] {msg}\n')


def _parse_landmark_to_bounding_box_str(landmark_annotation: Dict[str, Union[str, float, dict, list]],
                                        image_width: int, image_height: int) -> str:
    """Returns the bounding box landmark in its bounding box string representation.

    Parameters
    ----------
    landmark_annotation: dict[str, str or float or dict or list]
        Identified landmark annotation as a dictionary.
    image_width: int
        Image width.
    image_height: int
        Image height.

    Returns
    -------
    bounding_box_str: str
        String representing the identified landmark annotation.
    """
    sight_name = re.escape(landmark_annotation['description'].replace("'", "").replace('"', ''))
    bounding_box = landmark_annotation['boundingPoly']['vertices']

    x_vals = [point['x']/image_width for point in bounding_box]
    y_vals = [point['y']/image_height for point in bounding_box]
    ul_x, ul_y, lr_x, lr_y = min(x_vals), max(y_vals), max(x_vals), min(y_vals)
    ul_x = round(ul_x, ndigits=BOUNDING_BOX_DECIMALS_PRECISION)
    ul_y = round(ul_y, ndigits=BOUNDING_BOX_DECIMALS_PRECISION)
    lr_x = round(lr_x, ndigits=BOUNDING_BOX_DECIMALS_PRECISION)
    lr_y = round(lr_y, ndigits=BOUNDING_BOX_DECIMALS_PRECISION)

    return f'"({ul_x},{ul_y},{lr_x},{lr_y},{sight_name})"'


def _read_image_ids_for_labelling(city_name: str) -> Optional[List[int]]:
    """Returns the IDs of the images whose bounding box labels to find/label.

    Parameters
    ----------
    city_name: str
        Name of the city whose sights are to be labelled.

    Returns
    -------
    image_ids_to_label: list[int] or None
        List of image ids to label, None if no images are found for labelling.

    Notes
    -----
    Image IDs are retrieved at first to enable sequential processing instead of batch processing.
    The latter could very easily read to memory overflows on the ILS deployment server and is highly fault-intolerant.
    """
    max_google_vision_calls_per_new_city = int(environ['MAX_GOOGLE_VISION_CALLS_PER_NEW_CITY'])
    # random order by merely integers much faster than on whole table => subquery needed
    query = 'SELECT ids.id AS id ' \
            'FROM (' \
            'SELECT img.image_id AS id ' \
            'FROM integration_layer.dim_sights_images AS img, ' \
            'integration_layer.dim_sights_cities AS cities, ' \
            'integration_layer.fact_sights AS sights ' \
            'WHERE img.image_id = sights.image_id AND ' \
            'sights.city_id = cities.city_id AND ' \
            'img.image_labels IS NULL AND ' \
            f'cities.city_name = \'{city_name.upper()}\'' \
            ') AS ids ' \
            f'ORDER BY RANDOM() LIMIT {max_google_vision_calls_per_new_city}'
    image_ids_to_label = exec_dql_query(query, return_result=True)
    if image_ids_to_label is not None:
        image_ids_to_label = [id_tpl[0] for id_tpl in image_ids_to_label]

    return image_ids_to_label
