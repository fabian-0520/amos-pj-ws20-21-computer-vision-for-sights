"""This module contains various tests for the MTS trainer endpoint module."""
import os
import sys
import unittest
import pytest
import yaml
from mock import patch
from yolov5.trainer_endpoint import (
    generate_training_config_yaml,
    parse_bounding_boxes_encoding, persist_training_data, cleanup, upload_trained_model,
    _compute_actual_image_ids_to_load, _exec_dml_query, _exec_dql_query, _config, _get_raw_persisted_labels,
    _load_images_from_ids, _persist_image_and_label_files_batch, _preprocess_raw_label,
    _retrieve_label_mappings_raw_to_final, _retrieve_images_and_labels,
)
from yolov5.test_.test_models import ConnectionMock

sys.path.append('./..')


MODULE_PATH = 'yolov5.trainer_endpoint'
YAML_NAME = "sight_training_config.yaml"

class MTSCoreTestCase(unittest.TestCase):
    def tearDown(self) -> None:
        try:
            os.remove(YAML_NAME)
        except FileNotFoundError:
            print("yaml file wasn't found")

    def test_yaml_generation(self) -> None:
        sights = ["sight_a", "sight_b", "sight_c"]
        generate_training_config_yaml(sights)
        assert os.path.exists(YAML_NAME) == 1
        config_file = None
        with open(YAML_NAME, "r") as stream:
            try:
                config_file = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.assertEqual(3, config_file["nc"])
        self.assertEqual("sight_a", config_file["names"][0])

    @unittest.skip("only for testing endpoints")
    def test_download(self) -> None:
        os.environ["PGHOST"] = "abc"
        os.environ["PGPORT"] = "5432"
        os.environ["PGDATABASE"] = "abc"
        os.environ["PGUSER"] = "abv"
        os.environ["PGPASSWORD"] = "abc"
        os.environ["city"] = "berlin"
        persist_training_data()
        cleanup()

    def test_string_parser(self) -> None:
        example_string = '{"(0.135,0.725,0.825,0.015,\\"Brandenburger Tor\\")",' \
                         '"(0.1,0.5,0.3,0.2,\\"Siegessäule\\")"}'
        labels = parse_bounding_boxes_encoding(example_string)
        self.assertEqual(2, len(labels))
        self.assertEqual("BrandenburgerTor 0.48 0.63 0.69 0.71\n", labels[0][0])
        self.assertEqual("Siegessäule 0.2 0.65 0.2 0.3\n", labels[1][0])


class MTSHelperTestCase(unittest.TestCase):
    def test_persist_training_data(self) -> None:
        os.environ['city'] = 'new_york'
        with patch(f'{MODULE_PATH}._retrieve_images_and_labels') as input_receiver, \
                patch(f'{MODULE_PATH}.generate_training_config_yaml') as yaml_generator:

            persist_training_data()
            assert input_receiver.called
            assert yaml_generator.called

    def test_persist_training_data_no_city_set(self) -> None:
        os.environ['city'] = ''
        with pytest.raises(ValueError):
            persist_training_data()

    def test_upload_trained_model(self) -> None:
        os.environ['city'] = 'shanghai'
        with pytest.raises(FileNotFoundError):
            upload_trained_model()  # right execution branch if city set

    def test_upload_trained_model_no_city(self) -> None:
        os.environ['city'] = ''
        with pytest.raises(ValueError):
            upload_trained_model()  # no city passed

    def test_compute_actual_image_ids_to_load(self) -> None:
        with patch(f'{MODULE_PATH}._exec_dql_query', return_value=[(1,), (2,), (3,)]):
            label_mappings = {'BrooklynBridge': 'BrooklynBridge'}
            ids, excluded = _compute_actual_image_ids_to_load('new_york', label_mappings, 3)
            assert len(ids) == 3
            assert len(excluded) == 0

    def test_compute_actual_image_ids_to_load_too_few_labels(self) -> None:
        with patch(f'{MODULE_PATH}._exec_dql_query', return_value=[(1,), (2,), (3,)]):
            label_mappings = {'BrooklynBridge': 'BrooklynBridge'}
            ids, excluded = _compute_actual_image_ids_to_load('new_york', label_mappings, 30)
            assert len(ids) == 0
            assert excluded == ['BrooklynBridge']

    def test_valid_dql_query(self) -> None:
        with patch(f"{MODULE_PATH}.connect", return_value=ConnectionMock()) as conn_mock, \
                patch(f"{MODULE_PATH}._config", return_value={}) as config_mock:
            assert (conn_mock.called or config_mock.called) is False
            result = _exec_dql_query("SELECT abc FROM xyz", True)
            assert conn_mock.called and config_mock.called
            assert result == [["Berlin"], ["Tokyo"]]

    def test_valid_dml_query_no_payload(self) -> None:
        with patch(f"{MODULE_PATH}.connect", return_value=ConnectionMock()) as conn_mock, \
                patch(f"{MODULE_PATH}._config", return_value={}) as config_mock:
            dml_query, filling_parameters = 'INSERT INTO a VALUES ("b", "c")', None
            assert (conn_mock.called or config_mock.called) is False
            _exec_dml_query(dml_query, filling_parameters)
            assert conn_mock.called and config_mock.called

    def test_valid_dml_query_with_payload(self) -> None:
        with patch(f"{MODULE_PATH}.connect", return_value=ConnectionMock()) as conn_mock, \
                patch(f"{MODULE_PATH}._config", return_value={}) as config_mock:
            dml_query, filling_parameters = 'INSERT INTO a VALUES (%s, %s)', ('Tokyo', 'Berlin')
            assert (conn_mock.called or config_mock.called) is False
            _exec_dml_query(dml_query, filling_parameters)
            assert conn_mock.called and config_mock.called

    def test_config(self) -> None:
        os.environ['PGHOST'], os.environ['PGPORT'], os.environ['PGDATABASE'] = 'PGHOST', 'PGPORT', 'PGDATABASE'
        os.environ['PGUSER'], os.environ['PGPASSWORD'] = 'PGUSER', 'PGPASSWORD'
        db_dict = _config()

        for key in ["host", "port", "database", "user", "password"]:
            assert key in db_dict
            assert db_dict[key] == 'PG' + key.upper()

    def test_get_raw_persisted_labels(self) -> None:
        example_boxes = '{"(0.136,0.725,0.825,0.015,\\"Timessquare\\")",' \
                        '"(0.1,0.5,0.3,0.2,\\"Centralpark\\")"}'
        with patch(f'{MODULE_PATH}._exec_dql_query', return_value=[(example_boxes,)]):
            persisted_labels = _get_raw_persisted_labels('new_york')
            assert 'Timessquare' in persisted_labels
            assert 'Centralpark' in persisted_labels

    def test_load_images_from_ids(self) -> None:
        with patch(f'{MODULE_PATH}._exec_dql_query', return_value=[(b'test image', 'd812h3kfda8')]):
            mocked_result = _load_images_from_ids('new_york', [1])
            assert mocked_result is not None
            assert mocked_result[0] == (b'test image', 'd812h3kfda8')

    def test_persist_image_and_label_files_batch(self) -> None:
        with patch(f'{MODULE_PATH}._persist_single_image_and_label_file', return_value=True):
            example_nyc_boxes = '{"(0.12116,0.715,0.825,0.015,\\"Rockefellercenter\\")",' \
                                '"(0.1,0.6,0.5,0.2,\\"Statueofliberty\\")"}'
            example_box_fail = '{"(0.12116,0.715,0.825,0.015,\\"Grandcanyon\\")"}'
            images = [(b'img 1', example_nyc_boxes), (b'img2', example_nyc_boxes),
                      (b'img 3', None), (b'img 4', example_box_fail)]
            label_mapping = {'Rockefellercenter': 'RockefellerCenter',
                             'Statueofliberty': 'StatueOfLiberty',
                             'GrandCanyon': 'GrandCanyon'}
            excluded_raw_labels = ['Grandcanyon']
            final_sight_list = set()
            success_count = _persist_image_and_label_files_batch(images, label_mapping,
                                                                 excluded_raw_labels, final_sight_list)
            assert success_count == 3
            assert len(final_sight_list) == 2
            assert 'RockefellerCenter' in final_sight_list
            assert 'StatueOfLiberty' in final_sight_list

    def test_preprocess_raw_label(self) -> None:
        assert _preprocess_raw_label('HollywoodSignLos_Angeles') == 'HOLLYWOODSIGNLOSANGELES'

    def test_retrieve_label_mappings_raw_to_final(self) -> None:
        label_list = ['THISISANAWEFULLYLONGSHENZENSIGHTLABEL.',
                      'THISISANAWEFULLYLONGSHENZENSIGHTLaBEL',
                      'SIGHTLABEL', 'Shenzen']
        city = 'Shenzen'
        mapping_table = _retrieve_label_mappings_raw_to_final(label_list, city)
        # first two labels are not alright: mapping needed!
        assert mapping_table[label_list[0]] == label_list[2]
        assert mapping_table[label_list[1]] == label_list[2]
        assert mapping_table[label_list[2]] == label_list[2]
        assert mapping_table[label_list[3]] == label_list[3]

    def test_retrieve_images_and_labels(self) -> None:
        target_labels, target_city = ['KaesestubeKarlsruhe', 'WurststubeKarlsruhe'], 'Karlsruhe'
        with patch(f'{MODULE_PATH}._init_directories_for_training'), \
             patch(f'{MODULE_PATH}._get_raw_persisted_labels',
                   return_value=target_labels), \
             patch(f'{MODULE_PATH}._replace_labels_in_label_files_with_index'), \
             patch(f'{MODULE_PATH}._persist_image_and_label_files_batch', return_value=10) as persistor, \
             patch(f'{MODULE_PATH}._get_all_loadable_image_ids', return_value=range(1, 3001)), \
             patch(f'{MODULE_PATH}._compute_actual_image_ids_to_load', return_value=(range(1, 1001), [])), \
             patch(f'{MODULE_PATH}._load_images_from_ids'):

            _retrieve_images_and_labels(target_city, 1)
            assert persistor.call_count == 10


if __name__ == "__main__":
    unittest.main()
