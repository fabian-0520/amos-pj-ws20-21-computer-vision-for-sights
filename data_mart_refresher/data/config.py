"""This module yields the configuration parameters to the external DWH."""
from configparser import ConfigParser
import os


def config(filename=None, section='postgresql'):
    """Reads an .ini file containing the DWH access parameters and returns them as a parsed dictionary.

    Parameters
    ----------
    filename: str or None, default=None
        File name of the .ini file containing the DWH connection parameters,
        None if .ini file lies in main directory.
    section: str
        Respective section in the .ini file.

    Returns
    -------
    db: dict
        Parsed dictionary containing the DWH connection parameters.
    """
    filename = f'{os.environ["PYTHONPATH"]}/database.ini' if filename is None else filename
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise ReferenceError(f'Section {section} not found in the {filename} file')

    return db
