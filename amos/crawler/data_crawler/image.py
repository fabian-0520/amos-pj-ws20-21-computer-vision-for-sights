from data_crawler.sql_exec import exec_sql
from typing import BinaryIO


def insert_image(
    sight_image: BinaryIO,
    sight_image_width: int,
    sight_image_height: int,
    sight_image_data_source: str,
    sight_city: str = "Berlin",
) -> None:
    sql = """INSERT INTO load_layer.sight_images (sight_image, sight_city, sight_image_width,
            sight_image_height, sight_image_data_source) VALUES (%s,%s,%s,%s,%s) RETURNING id
            """

    exec_sql(
        sql,
        (
            sight_image,
            sight_city,
            sight_image_width,
            sight_image_height,
            sight_image_data_source,
        ),
    )
