import psycopg2
from .config import config
from typing import BinaryIO


def insert(
    sight_image: BinaryIO,
    sight_image_width: int,
    sight_image_height: int,
    sight_image_data_source: str,
    sight_city: str = "Berlin",
) -> None:
    connection = None
    sql = """INSERT INTO load_layer.sight_images (sight_image, sight_city, sight_image_width,
            sight_image_height, sight_image_data_source) VALUES (%s,%s,%s,%s,%s) RETURNING id
            """
    params = config()
    with psycopg2.connect(**params) as connection:
        connection.autocommit = True

        with connection.cursor() as cursor:
            try:
                record_to_insert = (
                    sight_image,
                    sight_city,
                    sight_image_width,
                    sight_image_height,
                    sight_image_data_source,
                )
                cursor.execute(sql, record_to_insert)
                connection.commit()

            except Exception as exc:
                print("Error executing SQL: %s" % exc)

            finally:
                connection.commit()
                cursor.close()
                print("PostgreSQL connection is closed")


def getImageData():
    sql = """ SELECT * FROM integration_layer.dim_sights_images WHERE image_id = 5"""

    params = config()
    with psycopg2.connect(**params) as connection:
        connection.autocommit = True

        with connection.cursor() as cursor:
            try:
                cursor.execute(sql)
                row = cursor.fetchone()
                file = open("test.png", "wb")
                file.write(row[1])

                connection.commit()
            except Exception as exc:
                print("Error executing SQL: %s" % exc)

            finally:
                connection.commit()
                cursor.close()
                print("PostgreSQL connection is closed")


if __name__ == "__main__":
    getImageData()
