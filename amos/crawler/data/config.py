"""This module yields the configuration parameters to the external DWH."""
import os
from dotenv import load_dotenv

load_dotenv()


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
        env_variable = os.getenv("PG{0}".format(param.upper()))
        if env_variable is not None:
            db[param] = env_variable
        else:
            raise ReferenceError(f"Environment Variable {env_variable} not found")

    return db
