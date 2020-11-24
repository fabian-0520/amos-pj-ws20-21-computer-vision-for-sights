import psycopg2
import json
from .config import config
from typing import BinaryIO


def insert(
    sight_name: str,
    sight_image: bytes,
    sight_image_width: int,
    sight_image_height: int,
    sight_image_data_source: str,
    sight_city: str = "Berlin",
    sight_image_bounding_box_point_x1y1: tuple = (1, 1),
    sight_image_bounding_box_point_x2y2: tuple = (2, 2),
) -> None:
    connection = None
    sql = """INSERT INTO load_layer.sight_images (sight_name, sight_image, sight_city,sight_image_width,
            sight_image_height, sight_image_bounding_box_x1y1, sight_image_bounding_box_x2y2,
            sight_image_data_source) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
            """
    params = config()
    with psycopg2.connect(**params) as connection:
        connection.autocommit = True

        with connection.cursor() as cursor:
            try:
                record_to_insert = (
                    sight_name,
                    sight_image,
                    sight_city,
                    sight_image_width,
                    sight_image_height,
                    "{0}".format(sight_image_bounding_box_point_x1y1),
                    "{0}".format(sight_image_bounding_box_point_x2y2),
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
    sql = """ SELECT * FROM data_mart_layer.images_berlin """

    params = config()
    with psycopg2.connect(**params) as connection:
        connection.autocommit = True

        with connection.cursor() as cursor:
            try:
                cursor.execute(sql)
                row = cursor.fetchone()
                file = open("binfile.png", "wb")
                file.write(row[0])
                print(row)
                connection.commit()
            except Exception as exc:
                print("Error executing SQL: %s" % exc)

            finally:
                connection.commit()
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")


def getRecordData():
    with open("./dwh/tests/fixtures/data.json") as f:
        data = json.load(f)
        f = open(data["sightImage"], "rb")
        filedata = f.read()
        data_record = (
            data["sightName"],
            filedata,
            data["sightCity"],
            data["sightImageResolution"],
            data["sightImageDataSource"],
        )
        return data_record


if __name__ == "__main__":
    file = open("download/Alexanderplatz/google_0002.jpg", "rb")
    data = file.read()
    getImageData()
