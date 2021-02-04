"""This module contains the trainer endpoint which is the main orchestrator for the MTS model training process."""
import glob
import imghdr
import os
import re
import shutil
from io import BytesIO
from itertools import combinations
from typing import Optional, Tuple, List, Dict
from fuzzywuzzy import fuzz
from psycopg2 import connect
from psycopg2._psycopg import Binary


def config():
    """Reads environment variables needed as DWH access parameters and returns them as a parsed dictionary.

    Returns
    -------
    db: dict[str, str]
        Parsed dictionary containing the DWH connection parameters.

    Raises
    ------
    ReferenceError
        If a required environment variable has not been found.
    """
    database_params, params = {}, ["host", "port", "database", "user", "password"]

    for param in params:
        env_variable_name = "PG{0}".format(param.upper())
        env_variable = os.getenv(env_variable_name)
        if env_variable is not None:
            database_params[param] = env_variable
        else:
            raise ReferenceError(f"Environment Variable {env_variable_name} not found")

    return database_params


def cleanup():
    """Cleans up created training data directory and its contents.

    Raises
    ------
    OSError
        If any deletions went wrong.
    """
    try:
        shutil.rmtree("../training_data")
    except OSError as exception:
        print("Error deleting training data: %s" % exception.strerror)

    try:
        shutil.rmtree("./runs")
    except OSError as exception:
        print("Error deleting runs: %s" % exception.strerror)

    try:
        os.remove("tmp.pt")
    except OSError as exception:
        print("Error deleting tmp.pt: %s" % exception.strerror)


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


def exec_dql_query(postgres_sql_string: str, return_result=False) -> Optional[object]:
    """Executes a given PostgreSQL query on the data warehouse and potentially returns the query result.

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


def generate_training_config_yaml(sights: List[str]) -> None:
    """Generates a .yaml configuration file which is used to generate classes and
    other information for model training.

    Parameters
    ----------
    sights: list[str]
        List of sight classes used for training the model.
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


def load_images_for_city(city_name: str) -> Optional[List[Tuple[bytes, str]]]:
    """Loads all images with corresponding labels for a given city.

    Parameters
    ----------
    city_name: str
        The name of the city the request is performed.

    Returns
    -------
    The list of tuples with an image file and the corresponding label .txt file.
    """
    query = f"select image_file, image_labels from data_mart_layer.images_{city_name}"
    return exec_dql_query(query, True)


def parse_bounding_box_string(labels_string: str) -> List[Tuple[str, str]]:
    """Parses a custom DWH bounding box string into potentially multiple tuples of
    bounding box encoding and label name.

    Parameters
    ----------
    labels_string: str
        String containing the bounding box string.

    Returns
    -------
    label_list: list[tuple[str, str]]
        List containing tuples of bounding box encoding and their label.
    """
    label_list, labels = [], re.findall("\\((.*?)\\)", labels_string)
    for label in labels:
        box_encoding_elements = label.split(",")
        _label = box_encoding_elements[-1].title().replace(" ", "").replace("\\", "").replace('"', "")
        re.sub(r"[^\x00-\x7F]+", "", _label)  # replace non-ascii characters inside label

        # parse coordinates
        ul_x, lr_x = float(box_encoding_elements[0]), float(box_encoding_elements[2])
        # Yolov5's y coordinate system is flipped!
        ul_y, lr_y = 1 - float(box_encoding_elements[1]), 1 - float(box_encoding_elements[3])
        x_width = round(abs(lr_x - ul_x), ndigits=6)  # abs for higher fault tolerance
        y_height = round(abs(ul_y - lr_y), ndigits=6)  # rounding speeds up model training
        x_center = round(ul_x + x_width/2, ndigits=6)
        y_center = round(ul_y + y_height/2, ndigits=6)

        # persist the results
        label_list.append((f"{_label} {x_center} {y_center} {x_width} {y_height}\n", _label))
    return label_list


def persist_training_data() -> None:
    """Generic method to load images, store them and generate a config file for training.

    Raises
    ------
    ValueError
        If no city has been passed.
    """
    city = os.getenv("city", "")

    if len(city) > 0:
        print(f"Starting image download for {city}")
        images = load_images_for_city(city)
        print(f"Fetched {len(images)} images")
        sight_names = save_images(images)
        generate_training_config_yaml(sight_names)
    else:
        raise ValueError('No city passed!')


def prepare_directories_for_training():
    """Prepares the directory for training"""
    try:
        os.makedirs("../training_data/images")
        os.makedirs("../training_data/labels")
    except FileExistsError:
        print("Directories exist")


def preprocess_label(label: str, city: str) -> str:
    """Returns the pre-processed sight label of a given city.

    Parameters
    ----------
    label: str
        Raw label.
    city: str
        City the label belongs to.

    Returns
    -------
    preprocessed_label: str
        Pre-processed label.
    """
    return re.sub('[^A-Z]+', '', label.upper()).replace(f'{city}', '')


def replace_labels(labels: List[str]):
    """
    Replaces labels with their respective indexes
    Parameters
    ----------
    labels: the list of label strings
    -------

    """
    _dir = '../training_data/labels'
    for file in os.listdir("../training_data/labels"):
        with open(_dir + "/" + file) as _file:
            text = ""
            for line in _file.readlines():
                sections = line.split(" ")
                text += str(labels.index(sections[0])) + " " + " ".join(sections[1:])

        with open(_dir + "/" + file, "w") as _file:
            _file.write(text)


def retrieve_label_mappings(label_list: List[str], city: str) -> Dict[str, str]:
    """Returns the label mappings for a given list of labels and the according cities.

    Parameters
    ----------
    label_list: list[str]
        Available raw labels.
    city: str
        City to train on.

    Returns
    -------
    mapping_table: dict[str, str]
        Mapping table containing the raw label as keys and the labels to be mapped to as values.
    """
    city_preprocessed = re.sub('[^A-Z]+', '', city.upper())
    mapping_table = dict(zip(label_list, label_list))

    for tpl in combinations(label_list, 2):  # removes replicated pairs
        label_1, label_2 = tpl
        label_1_processed = preprocess_label(label_1, city_preprocessed)
        label_2_processed = preprocess_label(label_2, city_preprocessed)

        if label_1_processed in label_2_processed:  # retain abstracted labels more
            mapping_table[label_2] = label_1  # label_2: replaced by new mapping label_1
        elif label_2_processed in label_1_processed:
            mapping_table[label_1] = label_2  # label_1: replaced by new mapping label_2
        elif fuzz.ratio(label_1_processed, label_2_processed) >= 0.9 * 100:
            label_mapping = (label_1, label_2) if len(label_1_processed) > len(label_2_processed) \
                else (label_2, label_1)
            mapping_table[label_mapping[0]] = label_mapping[1]

    return mapping_table


def save_images(image_label_tuples: List[Tuple[bytes, str]]) -> List[str]:
    """Sorts the fetched images (according to their labels) into
    correct directories and generates a final labels list.

    Parameters
    ----------
    image_label_tuples: list[tuple[bytes, str]]
        List in which each item corresponds to an image and its bounding box encoding.

    Returns
    -------
    sight_list: list[str]
        Final label list.
    """
    prepare_directories_for_training()
    sight_list, success_count = [], 0

    for pair in image_label_tuples:
        if pair[0] is None or pair[1] is None:
            continue
        label_data = parse_bounding_box_string(pair[1])
        file_string = ""
        for label in label_data:
            sight_name = label[1]
            file_string += label[0]
            if sight_name not in sight_list:
                sight_list.append(sight_name)
        # create image file
        index = len(glob.glob("../training_data/images/*")) + 1
        with BytesIO(pair[0]) as _file:
            ext = imghdr.what(_file)
        if ext is None:
            print("Skipped image, couldn't read")
            continue
        try:
            image_file = open("../training_data/images/" + str(index) + "." + ext, "wb")
            image_file.write(pair[0])
            image_file.close()
        except IOError as exception:
            print(exception)
            continue
        # create label file
        try:
            label_file = open("../training_data/labels/" + str(index) + ".txt", "w")
            label_file.write(file_string)
            label_file.close()
        except IOError as exception:
            print(exception)
            continue
        success_count += 1
    print("replacing labels...")
    replace_labels(sight_list)
    print(f"The final sight list: {sight_list}")
    print(
        f"Downloaded {len(image_label_tuples)}, {success_count} were successfully saved"
    )
    return sight_list


def upload_trained_model() -> None:
    """Reads the previously trained model runs and uploads it to the DWH.

    Raises
    ------
    ValueError
        If no readily trained city model is available.
    """
    city = os.getenv("city", "")

    if len(city) > 0:
        # opening the files and reading as binary
        in_file = open("tmp.pt", "rb")
        data = in_file.read()
        in_file.close()
        # generating query
        dml_query = (
            "INSERT INTO load_layer.trained_models(city, trained_model, n_considered_images) "
            "VALUES (%s, %s, %s)"
        )
        # get amount of downloaded images
        image_count = len(glob.glob("../training_data/images/*"))
        # execute query to upload weights
        exec_dml_query(dml_query, (city, Binary(data), image_count))
    else:
        raise ValueError('No city passed!')


if __name__ == "__main__":
    persist_training_data()
