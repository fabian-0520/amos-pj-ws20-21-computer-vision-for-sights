"""This module contains the psycopg2 database programming interface that is used across the application."""
from typing import Optional
from data.config import config
from psycopg2 import connect


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
