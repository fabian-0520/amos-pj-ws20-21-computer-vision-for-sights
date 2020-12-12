"""This module contains the psycopg2 database programming interface that is used across the application."""
from typing import Optional, Tuple
from .config import config
from psycopg2 import connect


def exec_dql_query(postgres_sql_string: str, return_result=False) -> Optional[object]:
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
                print('Error executing SQL: %s' % exc)

            finally:
                cursor.close()

    return result


def exec_dml_query(dml_query: str, filling_parameters: Optional[Tuple[object]]) -> None:
    """Inserts a given set of image labels for the image of the PostgreSQL database corresponding to the source hash.

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
                print('Error executing SQL: %s' % exc)

            finally:
                cursor.close()
