import os
from typing import Optional, Tuple, List

from psycopg2 import connect
from psycopg2._psycopg import Binary

from amos.sight_detector.yolov5.utils.general import strip_optimizer


def generate_training_config_yaml(sights: List[str]) -> None:
    """
    Generates a .yaml configuration file which is used to generate classes and other information for model training.
    Parameters
    ----------
    sights: the list of sight classes used for training the model
    """
    # TODO: Nico, file generation and saving
    # nc -> len(sights)
    # train -> sights mapped to path directories
    # test -> same as train
    # names -> just the sights list



def load_images_for_city(city_name: str) -> Optional[List[Tuple[object]]]:
    """
    Loads all images with corresponding labels for a given city
    Parameters
    ----------
    city_name: str
        The name of the city the request is performed

    Returns
    -------
    The list of tuples with an image file and the corresponding label .txt file
    """
    query = f"select image_file, image_labels from data_mart_layer.images_{city_name}"
    return exec_sql_query(query, True)


def upload_trained_model(city_name: str, image_count: int) -> None:
    """
    Optimizes the trained model runs into a file and uploads it with corresponding data
    Parameters
    ----------
    city_name: str
        the name of the city the weights belong to
    image_count: int
        the amount of images used for training
    """
    # optimizes weights and saves them to tmp.pt
    strip_optimizer("runs/train/exp0_*/weights/best.pt", "tmp.pt")
    # opening the files and reading as binary
    in_file = open("tmp.pt", "rb")
    data = in_file.read()
    in_file.close()
    # performing query
    dml_query = "INSERT INTO load_layer.trained_models(city, trained_model, n_considered_images, mapping_table) " \
                "VALUES (%s, %s, %s, %s)"
    exec_dml_query(dml_query, (city_name, Binary(data), image_count, "{}"))


def exec_sql_query(postgres_sql_string: str, return_result=False) -> Optional[object]:
    """Executes a given PostgreSQL string on the data warehouse and potentially returns the query result.
    Parameters
    ----------
    postgres_sql_string: str
        PostgreSQL query to evaluate in the external DHW.
    return_result: bool, default=False
        Whether to return the query result.
    Returns
    -------
    result: str or None
        Query result.
    """
    result = None
    with connect(**config()) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            try:
                cursor.execute(postgres_sql_string)
                connection.commit()
                cursor_result = cursor.fetchall()
                result = cursor_result if (return_result and cursor_result is not None) else return_result
            except Exception as exc:
                print("Error executing SQL: %s" % exc)
            finally:
                cursor.close()
    return result


def exec_dml_query(dml_query: str, filling_parameters: Optional[Tuple]) -> None:
    """Inserts a trained weights file into the PostgreSQL database corresponding to the source hash.
    Parameters
    ----------
    dml_query: str
        SQL DML string.
    filling_parameters: tuple[object] or None
        Object to inject into the empty string, None if the dml query is already filled.
    """
    with connect(**config()) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            try:
                if filling_parameters is None:
                    cursor.execute(dml_query)
                else:
                    cursor.execute(dml_query, filling_parameters)
                connection.commit()
            except Exception as exc:
                print("Error executing SQL: %s" % exc)
            finally:
                cursor.close()


def config():
    """Reads environment variables needed for the DWH access parameters and returns them as a parsed dictionary.

    Returns
    -------
    db: dict
        Parsed dictionary containing the DWH connection parameters.
    """

    db = {}

    params = ["host", "port", "database", "user", "password"]

    for param in params:
        env_variable_name = "PG{0}".format(param.upper())
        env_variable = os.getenv(env_variable_name)
        if env_variable is not None:
            db[param] = env_variable
        else:
            raise ReferenceError(f"Environment Variable {env_variable_name} not found")

    return db
