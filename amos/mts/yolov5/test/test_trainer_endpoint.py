import os
import unittest

import yaml

from ..trainer_endpoint import (
    generate_training_config_yaml,
    parse_label_string, persist_training_data, cleanup,
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
        persist_training_data("berlin")
        cleanup()

    def test_string_parser(self):
        example_string = '{"(11,11,21,21,\\"Brandenburger Tor\\")","(15,15,25,25,\\"Siegessäule\\")"}'
        labels = parse_label_string(example_string)
        print(labels[0][0])
        self.assertEqual(2, len(labels))
        self.assertEqual("BrandenburgerTor 11 11 21 21\n", labels[0][0])
        self.assertEqual("Siegessäule", labels[1][1])


if __name__ == "__main__":
    unittest.main()
