How to: run/deploy the service via Docker
_________________________________________

1. Set <DATA_MART_MTS_ENDPOINT_URL> pointing to the available Model Training Service (MTS) endpoint
2. Set <DATA_MART_MTS_ENDPOINT_URL> pointing to the available Image Labelling Service (ILS) endpoint
3. Open the terminal
4. Move into the project directory (.../data_mart_refresher)
5. Build the Docker image: docker build -t data_mart_refresher .
6. Run the Docker image:
docker run  -e DATA_MART_MTS_ENDPOINT_URL=<DATA_MART_MTS_ENDPOINT_URL>
            -e DATA_MART_MTS_ENDPOINT_URL=<DATA_MART_MTS_ENDPOINT_URL>
            -e DATA_MART_REFRESH_DATA_MARTS_EVERY_SECONDS=5
            -e DATA_MART_ENABLE_MODEL_TRAINING_EVERY_SECONDS=10
            -e DATA_MART_ENABLE_LABELLING_REQUESTS_EVERY_SECONDS=10
            -it data_mart_refresher


How to: run tests incl. coverage
________________________________

1. Open the terminal
2. Move into the project directory (.../data_mart_refresher)
3. Run: coverage run -m pytest
