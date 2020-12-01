from data.config import config
from pytest import raises


def test_config():
    db_dict = config(filename='database.ini')
    assert len(db_dict) == 5

    for key in ['host', 'port', 'database', 'user', 'password']:
        assert key in db_dict


def test_config_error():
    with raises(ReferenceError):
        config('NOT EXISTING')
