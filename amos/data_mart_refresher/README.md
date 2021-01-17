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
      <IS_MTS_GPU_ENABLED>: whether the deployed MTS has GPU access
      <MIN_LABELLED_IMAGES_NEEDED_FOR_TRAINING>: minimum number of labelled images needed to trigger training
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
   docker run 
   -e ILS_PUBLIC_ENDPOINT_URL=http://test.de
   -e MTS_EC2_INSTANCE_ID=i-03a7d6be2beacdc11
   -e AWS_ACCESS_KEY_ID=AKIA2HXMTYK3IXGC4QOZ
   -e AWS_ACCESS_KEY=+qbfzFimxv03RRHJJFUfggtIJ/z8VQ/v4SouKqtX
   -e AWS_REGION=eu-central-1
   -e IS_MTS_GPU_ENABLED=False
   -e DATA_MART_REFRESH_DATA_MARTS_EVERY_SECONDS=5
   -e DATA_MART_ENABLE_MODEL_TRAINING_EVERY_SECONDS=60
   -e DATA_MART_ENABLE_LABELLING_REQUESTS_EVERY_SECONDS=10
   -e PGHOST=postgres.cxuqxclhqrjq.eu-central-1.rds.amazonaws.com
   -e PGDATABASE=postgres
   -e PGUSER=postgres
   -e PGPORT=5432
   -e PGPASSWORD=dwh-sight-scan
   -it data_mart_refresher


How to: run tests incl. coverage

---

1. Open the terminal
2. Move into the project directory (.../data_mart_refresher)
3. Run: coverage run -m pytest -v
4. Show coverage: coverage report
