import json

import psycopg2

from config import config


def helper():
    print("Hello World")


def insert_image():
    sql = """INSERT INTO load_layer.sight_images (sight_name, sight_image,sight_city, sight_image_resolution, 
    sight_image_data_source) VALUES (%s,%s,%s,%s,%s) RETURNING id"""
    connection = None
    try:
        params = config()
        connection = psycopg2.connect(**params)
        connection.autocommit = True
        cursor = connection.cursor()

        record_to_insert = getRecordData()
        cursor.execute(sql, record_to_insert)
        connection.commit()
        id = cursor.fetchone()[0]
        count = cursor.rowcount
        print("ID:", id, count)
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


def getRecordData():
    with open("./amos/tests/fixtures/data.json") as f:
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
    insert_image()
