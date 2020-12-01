"""This module contains the cron job business logic, i.e. triggering the external DWH,
Model Training Service (MTS) and Image Labelling Service (ILS)."""
from data.sql_exec import exec_sql
from os import environ
from requests import post
import schedule


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
        environ["ILS_ENDPOINT_URL"][:-1] if environ["ILS_ENDPOINT_URL"][-1] == "/" else environ["ILS_ENDPOINT_URL"]
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

    if not _notify_external_service(city_without_image_labels_query, ils_training_service_url, "new"):
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
        _notify_external_service(labeled_city_to_update, ils_training_service_url, "existing")


def trigger_city_model_training() -> None:
    """Triggers the model training service (MTS) if necessary by sending a
    POST request with the city name as a path parameter.
    """
    mts_training_service_url = (
        environ["MTS_ENDPOINT_URL"][:-1] if environ["MTS_ENDPOINT_URL"][-1] == "/" else environ["MTS_ENDPOINT_URL"]
    )
    city_without_model_query = """
        SELECT city_dim.city_name AS city_name
        FROM (SELECT dc_inner.city_id AS city_id, dc_inner.city_name AS city_name
              FROM integration_layer.fact_sights AS fs_inner,
                integration_layer.dim_sights_images AS di_inner,
                integration_layer.dim_sights_cities AS dc_inner
              WHERE fs_inner.image_id = di_inner.image_id AND fs_inner.city_id = dc_inner.city_id
                AND di_inner.image_labels IS NOT NULL
              ) AS city_dim
        LEFT JOIN integration_layer.fact_models model_facts ON city_dim.city_id = model_facts.city_id
        WHERE model_facts.city_id IS NULL ORDER BY model_facts.timestamp_id ASC LIMIT 1"""

    if not _notify_external_service(city_without_model_query, mts_training_service_url):
        city_model_to_be_updated_query = """
            SELECT city_model_to_update.city_name AS city_name
            FROM (SELECT images.available_training_size - models.last_training_size AS n_new_images,
                    dim_cities.city_name AS city_name
                  FROM (SELECT count(*) AS available_training_size, city_id AS city_id
                        FROM integration_layer.fact_sights AS fact_sights,
                            integration_layer.dim_sights_images AS dim_images
                        WHERE fact_sights.image_id = dim_images.image_id AND dim_images.image_labels IS NOT NULL
                        GROUP BY city_id) AS images,
                       (SELECT max(n_considered_images) AS last_training_size, inner_fact_models.city_id AS city_id
                        FROM integration_layer.dim_models_trained_models AS inner_dim_models,
                            integration_layer.fact_models AS inner_fact_models
                        WHERE inner_dim_models.trained_model_id = inner_fact_models.trained_model_id
                        GROUP BY inner_fact_models.city_id) AS models,
                        integration_layer.dim_sights_cities AS dim_cities
                  WHERE images.city_id = models.city_id AND models.city_id = dim_cities.city_id AND
                    images.available_training_size - models.last_training_size > 0
                  ORDER BY n_new_images DESC LIMIT 1) AS city_model_to_update
            WHERE n_new_images > 99
        """
        _notify_external_service(city_model_to_be_updated_query, mts_training_service_url)


def trigger_data_marts_refresh() -> None:
    """Triggers an update of all data marts included in the DWH."""
    postgres_fct_call = "SELECT RefreshAllMaterializedViews('data_mart_layer')"
    exec_sql(postgres_fct_call)


def _notify_external_service(dwh_sql: str, post_base_url: str, optional_path_param=None) -> bool:
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
        post(f"{post_base_url}/{result}{postfix}")
        external_service_notified = True

    return external_service_notified
