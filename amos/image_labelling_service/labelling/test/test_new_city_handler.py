from _pytest.monkeypatch import MonkeyPatch
from labelling.new_city_handler import persist_google_vision_labels, _get_image_resolution, \
    _get_merged_bounding_box_string, _label_image, _parse_landmark_to_bounding_box_str, _read_image_ids_for_labelling, \
    LOG_FILE_NAME, log_incident
from mock import patch
from typing import Dict, Union, List
import os

MODULE_PATH = 'labelling.new_city_handler'


def get_test_image_bytes() -> bytes:
    with open('labelling/test/test_image.png', 'rb') as image:
        return image.read()


def test_persist_google_vision_labels_images_available() -> None:
    with patch(f'{MODULE_PATH}._read_image_ids_for_labelling', return_value=[1, 2, 3]) as id_retriever, \
            patch(f'{MODULE_PATH}._label_image') as labeller, \
            patch(f'{MODULE_PATH}.log_incident'):  # omit logging for tests

        persist_google_vision_labels('berlin')
        assert id_retriever.called
        assert labeller.called
        assert labeller.call_count == 3


def test_persist_google_vision_labels_no_images_available() -> None:
    with patch(f'{MODULE_PATH}._read_image_ids_for_labelling', return_value=None) as id_retriever, \
            patch(f'{MODULE_PATH}.log_incident') as logger:  # omit logging for tests
        persist_google_vision_labels('berlin')
        assert id_retriever.called
        assert 'No images' in logger.call_args[0][0]


def test_get_image_resolution() -> None:
    width, height = _get_image_resolution(get_test_image_bytes())
    assert width == 950
    assert height == 672


def test_get_merged_bounding_box_string() -> None:
    loose_box_strings = [
        "(1,2,3,4,Test1)",
        "(2,3,4,5,Test2)",
        "(3,4,5,6,Test3)",
    ]
    actual_result = _get_merged_bounding_box_string(loose_box_strings)
    expected_result = '{' + f'{loose_box_strings[0]},{loose_box_strings[1]},{loose_box_strings[2]}' + '}'

    assert actual_result == expected_result


def test_label_image(vision_response_mock: List[Dict[str, Union[str, float, dict, list]]]) -> None:
    mock_url = 'https://xd.com/awesome.png'

    with patch(f'{MODULE_PATH}.exec_dql_query',
               return_value=[[get_test_image_bytes(), mock_url]]), \
         patch(f'{MODULE_PATH}._get_landmarks_from_vision', return_value=vision_response_mock), \
         patch(f'{MODULE_PATH}.exec_dml_query') as persistor:
        _label_image(42)

        # no error occurring
        assert persistor.called
        called_query = persistor.call_args_list[0][0][0]

        # url extraction correct
        assert mock_url in called_query

        # both labels saved
        assert vision_response_mock[0]['description'] in called_query
        assert vision_response_mock[1]['description'] in called_query


def test_log_incident() -> None:
    if os.path.exists(LOG_FILE_NAME):
        os.remove(LOG_FILE_NAME)

    assert os.path.exists(LOG_FILE_NAME) is False
    log_incident('Test :)')
    assert os.path.exists(LOG_FILE_NAME) is True
    os.remove(LOG_FILE_NAME)


def test_parsing_landmark_to_str(vision_response_mock: List[Dict[str, Union[str, float, dict, list]]]) -> None:

    width, height = _get_image_resolution(get_test_image_bytes())
    test_landmark = vision_response_mock[1]
    bounding_box_infos = _parse_landmark_to_bounding_box_str(test_landmark, width, height)[2:-2].split(',')

    assert all(
        map(
            lambda relative_position: 0. < float(relative_position) < 1.,
            bounding_box_infos[:-1]
        )
    )

    assert bounding_box_infos[-1] == test_landmark['description']


def test_read_image_ids_for_labelling(monkeypatch: MonkeyPatch) -> None:
    with patch(f'{MODULE_PATH}.exec_dql_query', return_value=[(1,), (2,), (3,)]):
        image_ids_to_label = _read_image_ids_for_labelling('test city')
        assert image_ids_to_label is not None
        assert image_ids_to_label == [1, 2, 3]
