"""This module yields the configuration parameters to the external data warehouse."""
import os


def config():
    """Reads environment variables needed for the data warehouse access parameters and
    returns them as a parsed dictionary.

    Returns
    -------
    data: dict
        Parsed dictionary containing the data warehouse connection parameters.
    """

    db = {}
    params = ['host', 'port', 'database', 'user', 'password']

    for param in params:
        env_variable_name = f'PG{param.upper()}'
        env_variable = os.getenv(env_variable_name)
        if env_variable is not None:
            db[param] = env_variable
        else:
            raise ReferenceError(f'Environment Variable {env_variable_name} not found')

    return db
