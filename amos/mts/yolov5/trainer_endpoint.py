import glob
import imghdr
import os
import re
import shutil
from io import BytesIO
from typing import Optional, Tuple, List

from psycopg2 import connect
from psycopg2._psycopg import Binary


def persist_training_data(city_name: str) -> None:
    """
    Generic method to load images, store them and generate a config file for training
    Parameters
    ----------
    city_name: str
        name of the city to train for
    """
    images = load_images_for_city(city_name)
    sight_names = save_images(images)
    generate_training_config_yaml(sight_names)


def cleanup():
    """
    Cleans up created training data directory and its contents.
    """
    try:
        shutil.rmtree("../training_data")
    except OSError as e:
        print("Error deleting training data: %s" % e.strerror)


def load_images_for_city(city_name: str) -> Optional[List[Tuple[bytes, str]]]:
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


def parse_label_string(labels_string: str) -> List[Tuple[str, str]]:
    """
    parses a custom postgres label entity string into a tuple of label name and a label line in a label file
    Parameters
    ----------
    labels_string

    Returns
    -------
    List of tuples of [label_line (str), label_name (str)]
    """
    labels = re.findall("\\((.*?)\\)", labels_string)
    label_list = []
    for label in labels:
        elements = label.split(",")
        label = elements[-1]
        re.sub(r'[^\x00-\x7F]+', '', label)  # replace non-ascii characters inside label
        label_string = label.replace(" ", "") + " " + " ".join(elements[:-1]) + "\n"
        label_string = label_string.replace('"', "").replace("\\", "")
        label = label.replace('"', "").replace("\\", "").replace(" ", "")
        label_list.append((label_string, label))
    return label_list


def save_images(image_label_tuples: List[Tuple[bytes, str]]) -> List[str]:
    """
    Sorts fetched images according to their labels into correct directories and accordingly generates labels
    Parameters
    ----------
    image_label_tuples: list of tuples of image, label file

    Returns
    -------
    The list of labels
    """
    sight_list = []
    # create directories for training and test data
    try:
        os.makedirs("../training_data/images")
        os.makedirs("../training_data/labels")
    except FileExistsError:
        print("Directories exist")

    for pair in image_label_tuples:
        if pair[0] is None or pair[1] is None:
            continue
        label_data = parse_label_string(pair[1])
        file_string = ""
        for label in label_data:
            sight_name = label[1]
            file_string += label[0]
            if sight_name not in sight_list:
                sight_list.append(sight_name)
        # create image file
        index = len(glob.glob("../training_data/images/*")) + 1
        with BytesIO(pair[0]) as f:
            ext = imghdr.what(f)
        if ext is None:
            print("Skipped image, couldn't read")
            continue
        try:
            image_file = open("../training_data/images/" + str(index) + "." + ext, "wb")
            image_file.write(pair[0])
            image_file.close()
        except IOError as e:
            print(e)
            continue
        # create label file
        try:
            label_file = open("../training_data/labels/" + str(index) + ".txt", "w")
            label_file.write(file_string)
            label_file.close()
        except IOError as e:
            print(e)
    return sight_list


def generate_training_config_yaml(sights: List[str]) -> None:
    """
    Generates a .yaml configuration file which is used to generate classes and other information for model training.
    Parameters
    ----------
    sights: the list of sight classes used for training the model
    """
    yaml = open("./sight_training_config.yaml", "w")
    yaml.write("# train and val data\n")
    yaml.write("train: ../training_data/images\n")
    yaml.write("val: ../training_data/images\n\n")
    yaml.write("# number of classes\n")
    yaml.write("nc: " + str(len(sights)) + "\n\n")
    yaml.write("# class names\n")
    yaml.write("names: [" + ",".join(sights) + "]")
    yaml.close()


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
    # opening the files and reading as binary
    in_file = open("tmp.pt", "rb")
    data = in_file.read()
    in_file.close()
    # performing query
    dml_query = (
        "INSERT INTO load_layer.trained_models(city, trained_model, n_considered_images, mapping_table) "
        "VALUES (%s, %s, %s, %s)"
    )
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
                result = (
                    cursor_result
                    if (return_result and cursor_result is not None)
                    else return_result
                )
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
