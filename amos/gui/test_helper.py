from helper import wipe_prediction_input_images, get_current_prediction_output_path
import os


def test_wipe_prediction_input_images_new_dir():
    dummy_yolo_path, dummy_image_path = 'YOLO2/', 'IMAGES2/'
    dummy_full_path = dummy_yolo_path + dummy_image_path

    assert os.path.isdir(dummy_full_path) is False
    wipe_prediction_input_images(dummy_yolo_path + dummy_image_path)
    assert os.path.isdir(dummy_full_path) is True

    os.rmdir(f'./{dummy_yolo_path + dummy_image_path[:-1]}')
    os.rmdir('./' + dummy_yolo_path[:-1])


def test_wipe_prediction_input_images_existing_dir():
    dummy_yolo_path, dummy_image_path = 'YOLO/', 'IMAGES/'
    dummy_file_name = 'dummy_file.png'
    dummy_full_path = dummy_yolo_path + dummy_image_path + dummy_file_name

    os.makedirs(dummy_yolo_path + dummy_image_path)
    _create_file(dummy_full_path)
    wipe_prediction_input_images(dummy_yolo_path + dummy_image_path)

    assert os.path.isfile(dummy_full_path) is False

    os.rmdir(f'./{dummy_yolo_path + dummy_image_path[:-1]}')
    os.rmdir('./' + dummy_yolo_path[:-1])


def test_file_reload_new_dir():
    dummy_yolo_path, dummy_image_path = 'YOLO1/', 'IMAGES2/'
    dummy_composite_path = f'./{dummy_yolo_path}{dummy_image_path}'

    assert os.path.isdir(dummy_composite_path) is False

    os.makedirs(dummy_composite_path)
    result = get_current_prediction_output_path(dummy_yolo_path, dummy_image_path)

    assert 'IMAGES2' in result

    os.rmdir(dummy_composite_path)
    os.rmdir('./' + dummy_yolo_path[:-1])


def _create_file(dummy_full_path):
    with open(f'{os.getcwd()}/{dummy_full_path}', 'w+') as file:
        file.write('dummy')
