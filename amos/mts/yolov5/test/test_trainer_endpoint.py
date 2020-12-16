import os
import unittest
import yaml

from yolov5.trainer_endpoint import generate_training_config_yaml, save_images

from yolov5.trainer_endpoint import load_images_for_city


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

    def test_image_saving(self):
        labels = save_images([])
        self.assertEqual(0, len(labels))

    def test_temp(self):
        load_images_for_city('berlin')
        # returns e.g. '{"(11,11,21,21,\\" Brandenburger Tor\\")","(15,15,25,25,\\" Siegessäule\\")"}'

    # TODO: complete further tests for 100% code coverage


if __name__ == "__main__":
    unittest.main()
