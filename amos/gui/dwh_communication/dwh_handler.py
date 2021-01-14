"""This module contains necessary business logic in order to communicate with the dwh_communication warehouse."""
from dwh_communication.exec_dwh_sql import exec_dql_query
from typing import Optional
from json import loads

HTTP_400_MESSAGE = "Wrong request format - please refer to /api/swagger!"
HTTP_200_MESSAGE = "Request successfully executed."


def get_downloaded_model(city: str) -> Optional[bytes]:
    """Returns the downloaded and trained model for the specified city if it is available in the data warehouse.

    Parameters
    ----------
    city: str
        Name of the city.

    Returns
    -------
    found_model: bytes or None
        Retrieved .pt model file.
    """
    trained_model_query = (
        f"SELECT trained_model FROM data_mart_layer.current_trained_models " f"WHERE city_name = '{city.upper()}'"
    )
    found_model = exec_dql_query(trained_model_query, return_result=True)
    if found_model:
        return found_model[0][0].tobytes()

    return None





