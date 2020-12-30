"""This module contains the tests for the config module of the dwh_communication sub-app."""
from dwh_communication.config import config
from pytest import raises


def test_config():
    db_dict = config()
    assert len(db_dict) == 5

    for key in ["host", "port", "database", "user", "password"]:
        assert key in db_dict


def test_config_error(monkeypatch):
    monkeypatch.delenv("PG_HOST", raising=True)
    monkeypatch.delenv("PG_PORT", raising=True)
    monkeypatch.delenv("PG_DATABASE", raising=True)
    monkeypatch.delenv("PG_USER", raising=True)
    monkeypatch.delenv("PG_PASSWORD", raising=True)

    with raises(ReferenceError):
        config()
