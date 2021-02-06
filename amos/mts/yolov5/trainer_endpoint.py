"""This module contains the trainer endpoint which is the main orchestrator for the MTS model training process."""
import argparse
import glob
import imghdr
import os
import re
import shutil
from io import BytesIO
from itertools import combinations
from math import ceil
from time import sleep
from typing import Optional, Tuple, List, Dict, Set
from fuzzywuzzy import fuzz
from psycopg2 import connect
from psycopg2._psycopg import Binary


MAX_IMAGES_DOWNLOADED_PER_SINGLE_DATABASE_REQUEST = 100


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


def generate_training_config_yaml(sights: List[str]) -> None:
    """Generates a .yaml configuration file which is used to generate classes and
    other information for model training.

    Parameters
    ----------
    sights: list[str]
        List of sight classes used for training the model.
    """
    print('Generating final labels YAML file...')
    yaml = open("./sight_training_config.yaml", "w")
    yaml.write("# train and val data\n")
    yaml.write("train: ../training_data/images\n")
    yaml.write("val: ../training_data/images\n\n")
    yaml.write("# number of classes\n")
    yaml.write("nc: " + str(len(sights)) + "\n\n")
    yaml.write("# class names\n")
    yaml.write("names: [" + ",".join(sights) + "]")
    yaml.close()


def parse_bounding_boxes_encoding(labels_string: str) -> List[Tuple[str, str]]:
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


def persist_training_data(min_number_of_images_per_label: int = 30) -> None:
    """Generic method to load images, store them and generate a config file for training.

    Parameters
    ----------
    min_number_of_images_per_label: int, default=30
        Minimum number of images per label.

    Raises
    ------
    ValueError
        If no city has been passed.
    """
    city = os.getenv("city", "")

    if len(city) > 0:
        print(f"Investigating the data warehouse image contents for city {city.replace('_', ' ').title()}...")
        sight_names = _retrieve_images_and_labels(city, min_number_of_images_per_label)
        generate_training_config_yaml(sight_names)
    else:
        raise ValueError('No city passed!')


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
        _exec_dml_query(dml_query, (city, Binary(data), image_count))
    else:
        raise ValueError('No city passed!')


def _compute_actual_image_ids_to_load(city_name: str, label_mappings: Dict[str, str],
                                      min_number_of_images_per_label: int) -> Tuple[List[int], List[str]]:
    """Returns the relevant image ids to load after too sparse classes have been sorted out.

    Parameters
    ----------
    city_name: str
        Name of the city to train on.
    label_mappings: dict[str, str]
        Mappings between raw and final label.
    min_number_of_images_per_label: int
        Minimum number of images per label.

    Returns
    -------
    image_ids: list[int]
        Actual image ids to load.
    excluded_labels: list[str]
        List of labels to exclude from loading due to sparsity.
    """
    print('Computing sparse labels to exclude and restricting the set of relevant image ids...')
    image_ids, labels_excluded_from_training = [], []

    for final_label in set(label_mappings.values()):
        raw_labels = [raw_label for raw_label, _final_label in label_mappings.items()
                      if _final_label == final_label]
        upper_associated_raw_labels = [raw_label.upper() for raw_label, _final_label in label_mappings.items()
                                       if _final_label == final_label]
        query = f"""select image_id
                    from data_mart_layer.images_{city_name} city_mart
                    where image_labels is not null and exists (
                      select *
                      from unnest(city_mart.image_labels) as bounding_box
                      where upper(regexp_replace(
                         replace(replace(replace(bounding_box.box_label, ' ', ''), '\\', ''), '"', ''), 
                            '[^\\x00-\\x7F]+', '')) 
                        in {tuple(upper_associated_raw_labels)})""" \
            .replace(',))', '))')  # remove , at end of tuples from SQL syntax
        label_image_ids_cache = _exec_dql_query(query, return_result=True)
        sleep(0.1)  # delay to increase robustness
        if label_image_ids_cache is not None:
            belonging_ids = list(sum(label_image_ids_cache, ()))
            if len(belonging_ids) >= int(min_number_of_images_per_label):
                image_ids += belonging_ids
            else:
                labels_excluded_from_training += raw_labels

    return list(set(image_ids)), list(set(labels_excluded_from_training))


def _config():
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


def _exec_dml_query(dml_query: str, filling_parameters: Optional[Tuple]) -> None:
    """Inserts a trained weights file into the PostgreSQL database corresponding to the source hash.

    Parameters
    ----------
    dml_query: str
        SQL DML string.
    filling_parameters: tuple[object] or None
        Object to inject into the empty string, None if the dml query is already filled.
    """
    with connect(**_config()) as connection:
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


def _exec_dql_query(postgres_sql_string: str, return_result=False) -> Optional[object]:
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
    with connect(**_config()) as connection:
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


def _get_all_loadable_image_ids(city_name: str) -> Optional[List[int]]:
    """Loads all ids of images with corresponding labels for a given city.

    Parameters
    ----------
    city_name: str
        The name of the city the request is performed.

    Returns
    -------
    image_ids: list[int]
        List of image ids to load.
    """
    query = f"select image_id from data_mart_layer.images_{city_name} where image_labels is not null"
    return list(
        map(
            lambda result: result[0],
            _exec_dql_query(query, True)
        )
    )


def _get_raw_persisted_labels(city_name: str, image_ids: List[int]) -> List[str]:
    """Returns a flattened list of all available raw labels for the given set of image ids.

    Parameters
    ----------
    city_name: str
        Name of the city to train for.
    image_ids: int
        Image ids.

    Returns
    -------
    available_raw_labels: list[str]
        Available raw labels.
    """
    final_labels_list = set()
    query = f"select image_labels from data_mart_layer.images_{city_name} where image_id in {tuple(image_ids)}"
    result = list(
        filter(
            lambda res: res is not None,
            map(
                lambda _res: _res[0] if len(_res) > 0 else None,
                _exec_dql_query(query, True)
            )
        )
    )
    for bounding_box_encoding in result:
        for parsed_box in parse_bounding_boxes_encoding(bounding_box_encoding):
            final_labels_list.add(parsed_box[1])

    return list(final_labels_list)


def _init_directories_for_training():
    """Prepares the directory for training"""
    try:
        os.makedirs("../training_data/images")
        os.makedirs("../training_data/labels")
    except FileExistsError:
        print("Directories exist")


def _load_images_from_ids(city_name: str, image_ids: List[int]) -> List[Tuple[bytes, str]]:
    """Loads all images including labels for the given image ids and city.

    Parameters
    ----------
    city_name: str
        The name of the city the request is performed for.
    image_ids: list[int]
        Ids of the images to download.

    Returns
    -------
    images_to_download: list[tuple[bytes, str]]
        List of tuples with the image and the corresponding labels.
    """
    query = f"select image_file, image_labels from data_mart_layer.images_{city_name} " \
            f"where image_id in {tuple(image_ids)}"
    return _exec_dql_query(query, True)


def _persist_image_and_label_files_batch(images: List[Tuple[bytes, str]], label_mapping: Dict[str, str],
                                         excluded_raw_labels: List[str], final_sight_list: Set[str]) -> int:
    """Persists a given batch of actual image files and their associated labels.

    Parameters
    ----------
    images: list[tuple[bytes, str]]
        List containing the images and labels.
    label_mapping: dict[str, str]
        Label mapping table to eliminate poor labels.
    excluded_raw_labels: list[str]
        Raw labels that have been excluded from training due to sparsity.
    final_sight_list: set[str]
        Final set of sights needed for later yaml file creation.

    Returns
    -------
    success_count: int
        How many images were persisted successfully out of the given batch.
    """
    success_count = 0
    for image, bounding_boxes_encoding in images:
        if image is None or bounding_boxes_encoding is None:
            continue
        label_data, file_string = parse_bounding_boxes_encoding(bounding_boxes_encoding), ""

        for label in label_data:
            if label[1] in excluded_raw_labels:  # excluded labels should not be considered in the model
                continue

            sight_name = label_mapping[label[1]]
            file_string += label[0].replace(label[1], sight_name)
            final_sight_list.add(sight_name)

        # create image and label file
        success_count += 1 if _persist_single_image_and_label_file(image, file_string) else 0

    return success_count


def _persist_single_image_and_label_file(image: bytes, labels_file_content: str) -> bool:
    """Creates image and label files and returns whether both creations were successful.

    Parameters
    ----------
    image: bytes
        The image file in raw bytes format.
    labels_file_content: str
        The content to write to the label file.

    Returns
    -------
    is_successful: bool
        Whether both creations were successful.
    """
    index = len(glob.glob("../training_data/images/*")) + 1
    with BytesIO(image) as _file:
        ext = imghdr.what(_file)
    if ext is None:
        print("Skipped image due to unknown or proprietary format.")
        return False

    try:
        image_file = open("../training_data/images/" + str(index) + "." + ext, "wb")
        image_file.write(image)
        image_file.close()
    except IOError as exception:
        print(exception)
        return False

    # create label file
    try:
        label_file = open("../training_data/labels/" + str(index) + ".txt", "w")
        label_file.write(labels_file_content)
        label_file.close()
    except IOError as exception:
        print(exception)
        return False

    return True


def _preprocess_raw_label(label: str, city: str) -> str:
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
    return re.sub('[^A-Z0-9]+', '', label.upper()).replace(f'{city.replace("_", "").upper()}', '')


def _retrieve_label_mappings_raw_to_final(label_list: List[str], city: str) -> Dict[str, str]:
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
    print('Computing mappings for duplicate/ambiguous labels...')
    city_preprocessed = re.sub('[^A-Z]+', '', city.upper())
    mapping_table = dict(zip(label_list, label_list))

    for tpl in combinations(label_list, 2):  # removes replicated pairs
        label_1, label_2 = tpl
        label_1_processed = _preprocess_raw_label(label_1, city_preprocessed)
        label_2_processed = _preprocess_raw_label(label_2, city_preprocessed)

        if len(label_1_processed) == 0 or len(label_2_processed) == 0:
            continue

        if label_1_processed in label_2_processed and label_1_processed != label_2_processed:  # retain abstracted labels more
            mapping_table[label_2] = label_1  # label_2: replaced by new mapping label_1
        elif label_2_processed in label_1_processed and label_1_processed != label_2_processed:
            mapping_table[label_1] = label_2  # label_1: replaced by new mapping label_2
        elif fuzz.ratio(label_1_processed, label_2_processed) >= 0.9 * 100:
            label_mapping = (label_1, label_2) if len(label_1_processed) > len(label_2_processed) \
                else (label_2, label_1)
            mapping_table[label_mapping[0]] = label_mapping[1]

    return mapping_table


def _replace_labels_in_label_files_with_index(labels: List[str]):
    """Replaces labels with their respective indexes.

    Parameters
    ----------

    labels: list[str]
        List of label strings.
    """
    print("Replacing actual labels with their corresponding label indices...")
    _dir = '../training_data/labels'
    for file in os.listdir("../training_data/labels"):
        with open(_dir + "/" + file) as _file:
            text = ""
            for line in _file.readlines():
                sections = line.split(" ")
                text += str(labels.index(sections[0])) + " " + " ".join(sections[1:])

        with open(_dir + "/" + file, "w") as _file:
            _file.write(text)


def print_label_mappings(mapping_table: Dict[str, str]) -> None:
    """Merely prints the identified label mappings.

    Parameters
    ----------
    mapping_table: dict[str, str]
        Label map containing the original, raw labels as keys and their mapping as values.
    """
    for key, value in mapping_table.items():
        if key != value:
            print(f'Mapping identified: old label {key} -> new label {value}.')


def _retrieve_images_and_labels(city: str, min_number_of_images_per_label: int) -> List[str]:
    """Fetches the images (according to their labels) into
    correct directories and generates a final labels list.

    Parameters
    ----------
    city: str
        City to perform the training for.
    min_number_of_images_per_label: int
        Minimum number of images per label.

    Returns
    -------
    sight_list: list[str]
        Final label list.
    """
    _init_directories_for_training()

    # retrieve relevant image ids for partitioned processing
    image_ids_to_load = _get_all_loadable_image_ids(city)  # list of tuples with: image file + bounding box
    label_mappings = _retrieve_label_mappings_raw_to_final(_get_raw_persisted_labels(city, image_ids_to_load), city)
    print_label_mappings(label_mappings)
    image_ids_to_load, excluded_raw_labels = _compute_actual_image_ids_to_load(city,
                                                                               label_mappings,
                                                                               min_number_of_images_per_label)

    # retrieve and save relevant images including their labels
    n_download_iterations = int(ceil(len(image_ids_to_load)/MAX_IMAGES_DOWNLOADED_PER_SINGLE_DATABASE_REQUEST))
    success_count, final_sights_set = 0, set()

    for current_download in range(n_download_iterations):
        print(f'Downloading and persisting images including labels... '
              f'[iteration {current_download+1}/{n_download_iterations}]')
        start_idx = current_download * MAX_IMAGES_DOWNLOADED_PER_SINGLE_DATABASE_REQUEST
        end_idx = start_idx + MAX_IMAGES_DOWNLOADED_PER_SINGLE_DATABASE_REQUEST
        images = _load_images_from_ids(city, image_ids_to_load[start_idx:end_idx])
        success_count += _persist_image_and_label_files_batch(images, label_mappings,
                                                              excluded_raw_labels, final_sights_set)

    # map raw to final labels
    final_sights_list = list(
        map(
            lambda raw_sight: label_mappings[raw_sight],
            list(final_sights_set)
        )
    )
    _replace_labels_in_label_files_with_index(final_sights_list)
    print(f"\nImage/label retrieval result:\n{'-'*30}\n"
          f"Downloaded {len(image_ids_to_load)} relevant images "
          f"of which {success_count} were successfully saved "
          f"({round(success_count/len(image_ids_to_load), ndigits=3)*100:.2f}%). "
          f"Final sights list:\n{final_sights_list} ({len(final_sights_list)} classes).")

    return final_sights_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--min_images_per_label', type=str, default='30', help='min. number of images per label')
    opt = parser.parse_args()
    persist_training_data(10)
