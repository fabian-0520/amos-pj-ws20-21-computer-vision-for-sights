import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("ILS_PUBLIC_ENDPOINT_URL", "https://test_1.com/nothing")
    monkeypatch.setenv("PYTHONPATH", "/data_mart_refresher")
    monkeypatch.setenv("PGHOST", "test")
    monkeypatch.setenv("PGPORT", "test")
    monkeypatch.setenv("PGDATABASE", "test")
    monkeypatch.setenv("PGUSER", "test")
    monkeypatch.setenv("PGPASSWORD", "test")
    monkeypatch.setenv("IS_MTS_GPU_ENABLED", "True")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_ACCESS_KEY", "test")
    monkeypatch.setenv("AWS_REGION", "test")
    monkeypatch.setenv("MTS_EC2_INSTANCE_ID", "test")
    monkeypatch.setenv("DATA_MART_REFRESH_DATA_MARTS_EVERY_SECONDS", "44")
    monkeypatch.setenv("DATA_MART_ENABLE_MODEL_TRAINING_EVERY_SECONDS", "55")
    monkeypatch.setenv("DATA_MART_ENABLE_LABELLING_REQUESTS_EVERY_SECONDS", "66")
    monkeypatch.setenv("MIN_LABELLED_IMAGES_NEEDED_FOR_TRAINING", "100")
