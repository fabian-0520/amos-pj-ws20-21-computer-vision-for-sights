import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("MTS_ENDPOINT_URL", "https://test_1.com/nothing")
    monkeypatch.setenv("ILS_ENDPOINT_URL", "https://test_2.com/something")
    monkeypatch.setenv("PYTHONPATH", "/data_mart_refresher")
