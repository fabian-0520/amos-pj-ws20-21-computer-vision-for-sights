import os
from typing import Optional, Tuple, List

from psycopg2 import connect


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
    sql = f"""select image_file, image_labels from data_mart_layer.images_${city_name}"""
    return exec_sql(sql, True)


def exec_sql(postgres_sql_string: str, return_result=False) -> Optional[object]:
    """Executes a given PostgreSQL string on the DWH and potentially returns the query result.

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
                cursor_result = cursor.fetchone()
                result = cursor_result[0] if (return_result and cursor_result is not None) else return_result

            except Exception as exc:
                print("Error executing SQL: %s" % exc)

            finally:
                cursor.close()

    return result


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
