"""This module contains the cron job business logic, i.e. triggering the external DWH,
Model Training Service (MTS) and Image Labelling Service (ILS)."""
from cron_jobs.mts_ec2_communication import is_mts_ec2_instance_running, trigger_mts_training, \
    stop_mts_ec2_instance_after_training, boot_mts_ec2_instance
from data.sql_exec import exec_sql
from os import environ
from requests import post
import schedule
from threading import Thread
from typing import Optional


def start_cron_job(func, every_seconds):
    """Starts a given cron job executing the passes stateless function.

    Parameters
    ----------
    func: callable
        Stateless function to execute through the cron job.
    every_seconds: int
        Number of seconds between a cron job execution.
    """
    schedule.every(every_seconds).seconds.do(func)


def trigger_city_image_labelling() -> None:
    """Triggers the image labelling service (ILS) if necessary by sending a
    POST request with the city name as a path parameter.
    """
    ils_training_service_url = (
        environ["ILS_PUBLIC_ENDPOINT_URL"][:-1]
        if environ["ILS_PUBLIC_ENDPOINT_URL"][-1] == "/"
        else environ["ILS_PUBLIC_ENDPOINT_URL"]
    )
    city_without_image_labels_query = """
        SELECT dim_cities.city_name AS city_name
        FROM (SELECT fact_sights.city_id AS city_id, min(fact_sights.timestamp_id) AS insertion_timestamp
                FROM integration_layer.dim_sights_images AS dim_images,
                    integration_layer.fact_sights AS fact_sights
                WHERE fact_sights.image_id = dim_images.image_id AND dim_images.image_labels IS NULL
                GROUP BY fact_sights.city_id
                HAVING count(*) = (
                    SELECT count(*)
                    FROM integration_layer.fact_sights AS inner_sights
                    WHERE inner_sights.city_id = fact_sights.city_id)) AS completely_new,
            integration_layer.dim_sights_cities AS dim_cities
        WHERE dim_cities.city_id = completely_new.city_id
        ORDER BY completely_new.insertion_timestamp ASC limit 1"""

    if not _notify_external_ils(city_without_image_labels_query, ils_training_service_url):
        labeled_city_to_update = """
            SELECT dim_cities.city_name
            FROM (SELECT count(*) AS n_missing_labels, fact_sights.city_id AS city_id
                    FROM integration_layer.dim_sights_images AS dim_images,
                            integration_layer.fact_sights AS fact_sights
                    WHERE fact_sights.image_id = dim_images.image_id AND dim_images.image_labels IS NULL
                    GROUP BY city_id
                    ORDER BY n_missing_labels DESC limit 1) AS labeled_city_to_update,
                integration_layer.dim_sights_cities AS dim_cities
            WHERE dim_cities.city_id = labeled_city_to_update.city_id
        """
        _notify_external_ils(labeled_city_to_update, ils_training_service_url, "existing")


def trigger_city_model_training() -> None:
    """Triggers the model training service (MTS) if necessary by booting the EC2 GPU instance
    with the city name as a path parameter.
    """
    train_city = _get_city_name_for_training()
    # train_city = 'istanbul'  # uncomment for testing
    try:
        if train_city is not None and not is_mts_ec2_instance_running():
            # if train_city is not None:  # uncomment for testing
            boot_mts_ec2_instance()
            trigger_mts_training(train_city)
            stop_thread = Thread(target=stop_mts_ec2_instance_after_training, args=(train_city,))
            stop_thread.start()
    except Exception as e:
        print(f'Error occurred during MTS pipeline execution: {e}.')


def _get_city_name_for_training() -> Optional[str]:
    """Returns the city name needed for the next training process, None if no training is required.

    Returns
    -------
    train_city: str or None
        Name of the city to train for, None if no training should take place.
    """
    city_without_model_query = f"""
        SELECT DISTINCT(dim_cities.city_name) AS city_name
        FROM (
            SELECT fs_inner.city_id AS city_id
            FROM integration_layer.fact_sights AS fs_inner,
                 integration_layer.dim_sights_images AS di_inner
            WHERE fs_inner.image_id = di_inner.image_id AND di_inner.image_labels IS NOT NULL
            GROUP BY city_id
            HAVING count(*) > {int(environ['MIN_LABELLED_IMAGES_NEEDED_FOR_TRAINING'])}
        ) AS trainable_cities, integration_layer.dim_sights_cities AS dim_cities
        LEFT JOIN integration_layer.fact_models AS model_facts ON model_facts.city_id = dim_cities.city_id
        WHERE dim_cities.city_id = trainable_cities.city_id AND model_facts.trained_model_id IS NULL
        LIMIT 1
    """
    train_city = exec_sql(city_without_model_query, return_result=True)

    return train_city


def trigger_data_marts_refresh() -> None:
    """Triggers an update of all data marts included in the DWH."""
    postgres_fct_call = "SELECT RefreshAllMaterializedViews('data_mart_layer')"
    exec_sql(postgres_fct_call)


def _notify_external_ils(dwh_sql: str, post_base_url: str, optional_path_param=None) -> bool:
    """Potentially updates an external endpoint with the non-empty result of the passed SQL query
    as a path parameter and returns whether the notification was indeed executed.

    Parameters
    ----------
    dwh_sql: str
        PostgreSQL query for the external DWH.
    post_base_url: str
        Base URL of the external service to be notified with the query result.
    optional_path_param: str or None, default=None
        Optional path parameter to append at the end.

    Returns
    -------
    external_service_notified: bool
        Whether the notification was executed.
    """
    external_service_notified = False
    result = exec_sql(dwh_sql, return_result=True)

    if isinstance(result, str):
        postfix = f"/{optional_path_param}" if optional_path_param is not None else ""
        post(f"{post_base_url}/api/cities/{result}{postfix}")
        external_service_notified = True

    return external_service_notified
