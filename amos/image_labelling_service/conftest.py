import io
from typing import Tuple
import pytest
from PIL import Image


class CursorMock:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def execute(self, sql_string):
        pass

    def fetchall(self):
        return [['Berlin'], ['Tokyo']]

    def close(self):
        pass


class ConnectionMock:
    autocommit = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def cursor(self):
        return CursorMock()

    def commit(self):
        pass


class ConnectionExceptionMock:
    autocommit = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def cursor(self):
        return CursorExceptionMock()


class CursorExceptionMock(CursorMock):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def execute(self, sql_string):
        raise Exception('SELECT abc FROM xyz')


class ImageMock:
    size: Tuple[int, int] = None

    def __init__(self):
        self.size = (1920, 1080)

    def tobytes(self):
        return b'testtesttesttesttesttesttest'


class InMemoryUploadedFileMock:
    def __init__(self):
        pass

    def open(self):
        return ImageMock()


class MD5Mock:
    def __init__(self):
        pass

    def hexdigest(self):
        return b'testtesttesttesttesttesttest'


class ModelMock:
    def __init__(self):
        pass

    def tobytes(self):
        return b'ThisIsSomeGreatPytorchModel!'


def _get_labels_string():
    return '{"boundingBoxes": [{\"ulx\": 0.12122, ' \
           '\"uly\": 0.34212, ' \
           '\"lrx\": 0.33311, ' \
           '\"lry\": 0.12315, ' \
           '\"sightName\": \"Brandenburger Tor\"}, ' \
           '{\"ulx\": 0.12122, ' \
           '\"uly\": 0.34212, ' \
           '\"lrx\": 0.33311, ' \
           '\"lry\": 0.12315, ' \
           '\"sightName\": \"Siegessaeule\"}]}'


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv('PYTHONPATH', '/django_orchestrator')
    monkeypatch.setenv('PYTHONPATH', 'test')
    monkeypatch.setenv('PGHOST', 'test')
    monkeypatch.setenv('PGPORT', 'test')
    monkeypatch.setenv('PGDATABASE', 'test')
    monkeypatch.setenv('PGUSER', 'test')
    monkeypatch.setenv('PGPASSWORD', 'test')
    monkeypatch.setenv('MAX_GOOGLE_VISION_CALLS_PER_NEW_CITY', '100')


@pytest.fixture(scope='module')
def labels_mock():
    return _get_labels_string()


@pytest.fixture(scope='module')
def connection_mock():
    return ConnectionMock()


@pytest.fixture(scope='module')
def connection_exception_mock():
    return ConnectionExceptionMock()


@pytest.fixture(scope='function')
def image_mock():
    file = io.BytesIO()
    image = Image.new('RGBA', size=(1337, 1338), color=(155, 0, 0))
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file.read()


@pytest.fixture(scope='module')
def md5_mock():
    return MD5Mock()


@pytest.fixture(scope='module')
def vision_response_mock():
    return [
        {
            'description': 'Test Sight 1',
            'boundingPoly': {
                'vertices': [
                    {
                        'x': 100,
                        'y': 250
                    },
                    {
                        'x': 300,
                        'y': 200
                    },
                    {
                        'x': 300,
                        'y': 250
                    },
                    {
                        'x': 100,
                        'y': 200
                    }
                ]
            }
        },
        {
            'description': 'Test Sight 2',
            'boundingPoly': {
                'vertices': [
                    {
                        'x': 433,
                        'y': 500
                    },
                    {
                        'x': 300,
                        'y': 100
                    },
                    {
                        'x': 300,
                        'y': 500
                    },
                    {
                        'x': 433,
                        'y': 100
                    }
                ]
            }
        }
    ]
