from mock import patch
from data_crawler.image import insert_image



def triggered_exec_sql(sql, value):
    return (sql, value)


def test_image_insert():

    mock_data = {
        "sight_image": "test_data",
        "sight_image_width": 10,
        "sight_image_height": 10,
        "sight_image_data_source": "test_data",
        "sight_city": "test_data",
    }

    with patch("data_crawler.image.exec_sql", side_effect=triggered_exec_sql) as exec_sql_mock:
        assert (exec_sql_mock.called) is False
        result = insert_image(**mock_data)
        exec_sql_mock.assert_called_with(
            """INSERT INTO load_layer.sight_images (sight_image, sight_city, sight_image_width,
            sight_image_height, sight_image_data_source) VALUES (%s,%s,%s,%s,%s) RETURNING id
            """,
            (
                mock_data["sight_image"],
                mock_data["sight_city"],
                mock_data["sight_image_width"],
                mock_data["sight_image_height"],
                mock_data["sight_image_data_source"],
            ),
        )

        print(result)
