import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("DATA_MART_MTS_ENDPOINT_URL", "https://test_1.com/nothing")
    monkeypatch.setenv("DATA_MART_MTS_ENDPOINT_URL", "https://test_2.com/something")
    monkeypatch.setenv("PYTHONPATH", "/data_mart_refresher")
    monkeypatch.setenv("PGHOST", "test")
    monkeypatch.setenv("PGPORT", "test")
    monkeypatch.setenv("PGDATABASE", "test")
    monkeypatch.setenv("PGUSER", "test")
    monkeypatch.setenv("PGPASSWORD", "test")
