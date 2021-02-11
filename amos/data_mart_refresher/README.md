How to: run/deploy the DMR via Docker
=====================================

1. Determine environment variables 
   a.) ILS variables:
      <ILS_PUBLIC_ENDPOINT_URL>: Image Labelling Service (ILS) endpoint URL for retrieving labels
   b.) AWS/MTS variables:
      <MTS_EC2_INSTANCE_ID>: instance ID of the MTS EC2 instance
      <AWS_ACCESS_KEY_ID>: ID of AWS access key (needed for MTS access)
      <AWS_ACCESS_KEY>: AWS access key (needed for MTS access)
      <AWS_REGION>: AWS region (e.g. eu-central-1)
      <MTS_EPOCHS>: number of epochs the MTS should train
      <MIN_LABELLED_IMAGES_NEEDED_FOR_TRAINING>: minimum number of labelled images needed to trigger training
      <MIN_IMAGE_NUMBER_PER_LABEL>: minimum number of labelled images per class
   c.) CRON variables:
      <DATA_MART_REFRESH_DATA_MARTS_EVERY_SECONDS>: frequency for refreshing DWH data marts
      <DATA_MART_ENABLE_MODEL_TRAINING_EVERY_SECONDS>: frequency for triggering model trainings
      <DATA_MART_ENABLE_LABELLING_REQUESTS_EVERY_SECONDS>: frequency for retrieving image labels
   d.) DWH connection parameters
      <PGHOST>
      <PGDATABASE>
      <PGUSER>
      <PGPORT>
      <PGPASSWORD>
2. Place the SSH key of the MTS EC2 instance is the project root directory and name it "ec2key.pem".
3. Open the terminal
4. Move into the project directory (.../data_mart_refresher)
5. Build the Docker image: docker build -t data_mart_refresher .
6. Run the Docker image:
   sudo docker run -d -e ILS_PUBLIC_ENDPOINT_URL=<ILS_PUBLIC_ENDPOINT_URL> -e MTS_EC2_INSTANCE_ID=<MTS_EC2_INSTANCE_ID> -e AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID> -e AWS_ACCESS_KEY=<AWS_ACCESS_KEY> -e AWS_REGION=<AWS_REGION> -e MTS_EPOCHS=<MTS_EPOCHS> -e DATA_MART_REFRESH_DATA_MARTS_EVERY_SECONDS=<DATA_MART_REFRESH_DATA_MARTS_EVERY_SECONDS> -e DATA_MART_ENABLE_MODEL_TRAINING_EVERY_SECONDS=<DATA_MART_ENABLE_MODEL_TRAINING_EVERY_SECONDS> -e DATA_MART_ENABLE_LABELLING_REQUESTS_EVERY_SECONDS=<DATA_MART_ENABLE_LABELLING_REQUESTS_EVERY_SECONDS> -e PGHOST=<PGHOST> -e PGDATABASE=<PGDATABASE> -e PGUSER=<PGUSER> -e PGPORT=<PGPORT> -e PGPASSWORD=<PGPASSWORD> -e MIN_LABELLED_IMAGES_NEEDED_FOR_TRAINING=<MIN_LABELLED_IMAGES_NEEDED_FOR_TRAINING> -e MIN_IMAGE_NUMBER_PER_LABEL=<MIN_IMAGE_NUMBER_PER_LABEL> -it data_mart_refresher


How to: run tests incl. coverage
================================

1. Open the terminal
2. Move into the project directory (.../data_mart_refresher)
3. Run: coverage run -m pytest -v
4. Show coverage: coverage report
