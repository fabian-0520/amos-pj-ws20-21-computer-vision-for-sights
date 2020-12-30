"""This module contains necessary business logic in order to communicate with the dwh_communication warehouse."""
from dwh_communication.exec_dwh_sql import exec_dml_query
from json import loads


def upload_image_labels(labels: str, source_hash: str) -> None:
    """Uploads the given labels for the specified image lookup hash.

    Parameters
    ----------
    labels: str
        JSON string containing the bounding box labels.
    source_hash: str
        Image lookup hash.
    """
    filled_dml_query = _get_image_label_dml_query(labels, source_hash)
    exec_dml_query(filled_dml_query, None)


def _get_image_label_dml_query(labels: str, source_hash: str) -> str:
    """Returns the prepared DML query necessary to insert the passed labels
    for the image corresponding to the passed lookup key.

    Parameters
    ----------
    labels: str
        Bounding box labels.
    source_hash: str
        Image lookup hash.

    Returns
    -------
    dml_query: str
        Prepared DML query for the label insertion.
    """
    bounding_boxes_input_dict = loads(labels)
    n_bounding_boxes = len(bounding_boxes_input_dict["boundingBoxes"])
    bounding_boxes_postgres_output_string = "{"

    for bounding_box_idx in range(n_bounding_boxes):
        bounding_box = bounding_boxes_input_dict["boundingBoxes"][bounding_box_idx]
        bounding_boxes_postgres_output_string += (
            f'"({bounding_box["ulx"]},{bounding_box["uly"]},'
            f'{bounding_box["lrx"]},{bounding_box["lry"]},'
            f'{bounding_box["sightName"]})"'
        )
        if bounding_box_idx < n_bounding_boxes - 1:  # still bounding boxes to come
            bounding_boxes_postgres_output_string += ","

    bounding_boxes_postgres_output_string += "}"

    return (
        "INSERT INTO load_layer.sight_image_labels(sight_image_data_source, sight_labels) "
        f"VALUES ('{source_hash}', '{bounding_boxes_postgres_output_string}')"
    )
