How to: run/deploy the service via Docker
_________________________________________

1. Set <MTS_ENDPOINT_URL> pointing to the available Model Training Service (MTS) endpoint
2. Set <ILS_ENDPOINT_URL> pointing to the available Image Labelling Service (ILS) endpoint
3. Open the terminal
4. Move into the project directory (.../data_mart_refresher)
5. Build the Docker image: docker build -t data_mart_refresher .
6. Run the Docker image:
docker run  -e MTS_ENDPOINT_URL=<MTS_ENDPOINT_URL>
            -e ILS_ENDPOINT_URL=<ILS_ENDPOINT_URL>
            -e REFRESH_DATA_MARTS_EVERY_SECONDS=5 
            -e ENABLE_MODEL_TRAINING_EVERY_SECONDS=10 
            -it data_mart_refresher
            
            
How to: run tests incl. coverage
________________________________

1. Open the terminal
2. Move into the project directory (.../data_mart_refresher)
3. Run: coverage run -m pytest
