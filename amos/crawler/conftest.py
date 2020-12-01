import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("PGHOST", "test")
    monkeypatch.setenv("PGPORT", "test")
    monkeypatch.setenv("PGDATABASE", "test")
    monkeypatch.setenv("PGUSER", "test")
    monkeypatch.setenv("PGPASSWORD", "test")
