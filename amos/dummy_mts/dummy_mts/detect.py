from time import sleep
from psycopg2 import connect
import os

config = {'host': os.environ['PGHOST'],
          'port': os.environ['PGPORT'],
          'database': os.environ['PGDATABASE'],
          'user': os.environ['PGUSER'],
          'password': os.environ['PGPASSWORD']}

dml_query_city = 'INSERT INTO load_layer.sight_images(sight_image, sight_city, sight_image_height, ' \
                 'sight_image_width, sight_image_data_source) ' \
                 'VALUES (%s, %s, %s, %s, %s)'
dml_query_model = 'INSERT INTO load_layer.trained_models(city, trained_model, n_considered_images, mapping_table) ' \
                  'VALUES (%s, %s, %s, %s)'

print('START TRAINING! ')
sleep(5)  # simulate training

with connect(**config) as connection:
    connection.autocommit = True
    with connection.cursor() as cursor:
        try:
            cursor.execute(dml_query_city, ('test image', os.environ['city'], 1080, 1920,
                                            f'mts-deployment-test-{os.environ["city"]}'))
            connection.commit()
            cursor.execute(dml_query_model, (os.environ['city'], b'12345', 10000, '{}'))
            connection.commit()
        except Exception as exc:
            print('Error executing SQL: %s' % exc)

        finally:
            cursor.close()

print('DONE! ')
