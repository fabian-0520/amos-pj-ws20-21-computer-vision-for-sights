import os
import unittest

import yaml
import sys
sys.path.append('./..')
from yolov5.trainer_endpoint import (
    generate_training_config_yaml,
    parse_bounding_box_string, persist_training_data, cleanup,
)


class MTSTestCase(unittest.TestCase):
    def tearDown(self) -> None:
        try:
            os.remove("sight_training_config.yaml")
        except FileNotFoundError:
            print("yaml file wasn't found")

    def test_yaml_generation(self):
        sights = ["sight_a", "sight_b", "sight_c"]
        generate_training_config_yaml(sights)
        assert os.path.exists("sight_training_config.yaml") == 1
        config_file = None
        with open("sight_training_config.yaml", "r") as stream:
            try:
                config_file = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.assertEqual(3, config_file["nc"])
        self.assertEqual("sight_a", config_file["names"][0])

    @unittest.skip("only for testing endpoints")
    def test_download(self):
        os.environ["PGHOST"] = "abc"
        os.environ["PGPORT"] = "5432"
        os.environ["PGDATABASE"] = "abc"
        os.environ["PGUSER"] = "abv"
        os.environ["PGPASSWORD"] = "abc"
        os.environ["city"] = "berlin"
        persist_training_data()
        cleanup()

    def test_string_parser(self):
        example_string = '{"(0.135,0.725,0.825,0.015,\\"Brandenburger Tor\\")",' \
                         '"(0.1,0.5,0.3,0.2,\\"Siegessäule\\")"}'
        labels = parse_bounding_box_string(example_string)
        self.assertEqual(2, len(labels))
        self.assertEqual("BrandenburgerTor 0.48 0.63 0.69 0.71\n", labels[0][0])
        self.assertEqual("Siegessäule 0.2 0.65 0.2 0.3\n", labels[1][0])


if __name__ == "__main__":
    unittest.main()
