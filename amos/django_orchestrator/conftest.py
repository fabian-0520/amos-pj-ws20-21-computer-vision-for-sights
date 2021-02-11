from typing import Tuple
import pytest


class InMemoryUploadedFileMock:
    content_type: str = None

    def __init__(self):
        self.content_type = 'image/png'

    def open(self):
        return ImageMock()


class RequestMock:
    FILES: dict = None

    def __init__(self):
        self.FILES = {'image': 'some Image'}


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
    file: bytes = b'testtesttesttesttesttesttest'

    def __init__(self):
        self.size = (1920, 1080)

    def tobytes(self):
        return b'testtesttesttesttesttesttest'


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


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv('PYTHONPATH', '/django_orchestrator')
    monkeypatch.setenv('PYTHONPATH', 'test')
    monkeypatch.setenv('PGHOST', 'test')
    monkeypatch.setenv('PGPORT', 'test')
    monkeypatch.setenv('PGDATABASE', 'test')
    monkeypatch.setenv('PGUSER', 'test')
    monkeypatch.setenv('PGPASSWORD', 'test')
    monkeypatch.setenv('MAX_SIGHTS_PER_CITY', 'test_max_sights')
    monkeypatch.setenv('MAX_IMAGES_PER_SIGHT', 'test_max_images')
    monkeypatch.setenv('MAPS_KEY', 'test_key')
    monkeypatch.setenv('IC_URL', 'test_ic_url')


@pytest.fixture(scope='module')
def in_memory_uploaded_file_mock():
    return InMemoryUploadedFileMock()


@pytest.fixture(scope='module')
def connection_mock():
    return ConnectionMock()


@pytest.fixture(scope='module')
def connection_exception_mock():
    return ConnectionExceptionMock()


@pytest.fixture(scope='module')
def image_mock():
    return ImageMock()


@pytest.fixture(scope='module')
def md5_mock():
    return MD5Mock()


@pytest.fixture(scope='module')
def model_mock():
    return ModelMock()
