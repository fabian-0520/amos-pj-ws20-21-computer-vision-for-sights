import pytest
from mock import patch
from time import sleep
from schedule import run_pending


def test_start_cron_job():
    from cron_jobs.jobs import start_cron_job  # needs to stay in here in order for environment patches to work
    stateful_cache = []

    def _closure_fct():
        stateful_cache.append("hello!")

    start_cron_job(_closure_fct, 1)
    sleep(1)
    run_pending()

    assert stateful_cache == ["hello!"]


@pytest.mark.parametrize("no_city_label_yet", [True, False])
def test_trigger_city_image_labelling(no_city_label_yet):
    from cron_jobs.jobs import trigger_city_image_labelling

    with patch("cron_jobs.jobs._notify_external_ils", return_value=no_city_label_yet) as notifier:
        assert notifier.called is False
        trigger_city_image_labelling()
        assert notifier.called


def test_trigger_data_marts_refresh():
    from cron_jobs.jobs import trigger_data_marts_refresh

    with patch("cron_jobs.jobs.exec_sql") as exec_sql:
        assert exec_sql.called is False
        trigger_data_marts_refresh()
        assert exec_sql.called
        assert exec_sql.call_args[0][0] == "SELECT RefreshAllMaterializedViews('data_mart_layer')"


@pytest.mark.parametrize(
    "exec_sql_result, expected_post_called, expected_fct_result", [("Berlin", True, True), (None, False, False)]
)
def test_notify_external_ils_with_query_result(exec_sql_result, expected_post_called, expected_fct_result):
    from cron_jobs.jobs import _notify_external_ils

    with patch("cron_jobs.jobs.exec_sql", return_value=exec_sql_result) as exec_sql, patch(
        "cron_jobs.jobs.post"
    ) as post:
        assert (exec_sql.called or post.called) is False
        result = _notify_external_ils("SELECT * from ABC", "https://www.com.de/")
        assert (exec_sql.called and post.called) is expected_post_called
        assert result is expected_fct_result
