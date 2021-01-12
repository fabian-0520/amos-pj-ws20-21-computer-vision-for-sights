How To: Deploying ILS, DOS, and DMR Services on AWS using EC2 (using macOS or Linux) 
==================================================================================== 

PREREQUISITES: 
--------------
MTS component is readily deployed and publicly accessible through an URL.


Step 0: Launch an EC2 instance running Ubuntu, preferrably with 8GB of RAM (otherwise, Docker problems may arise), and make sure the security group allows custom TCP traffic on ports 8001, 8002 from 0.0.0.0/0 and ::/0 (anywhere)
![Alt text](https://i.ibb.co/xjZ6wtc/Screenshot-2021-01-12-at-16-55-30.png)
Step 1: Replace variables of form <...> below with real values
    - <EC2_IP> := IP of the running EC2 instance
    - <EC2_URL> := URL of the running EC2 instance (always in the form "ec2-xxx-xxx-xxx-xxx.eu-central-1.compute.amazonaws.com", where xxx-xxx-xxx-xxx is the corresponding IP address)
    - <PG_HOST> := DWH host
    - <PG_DATABASE> := DWH database
    - <PG_USER> := DWH user
    - <PG_PORT> := DWH port
    - <PG_PASSWORD> := DWH password
    - <MAX_GOOGLE_VISION_CALLS_PER_NEW_CITY> := max. number of allowed Vision API calls for each new supported city that has yet no labels in the DWH
    - <MTS_URL> := URL of the MTS component
Step 2: Place your private SSH key for accessing the EC2 instance in your Downloads folder and rename it to "ec2key.pem"
Step 3: Prepare folder structures and install Docker on EC2 instance through SSH
    - sudo ssh -i ~/Downloads/ec2key.pem ubuntu@<EC2_IP>
    - sudo mkdir ils
    - sudo chmod 777 ils
    - sudo mkdir dos
    - sudo chmod 777 dos
    - sudo mkdir dmr
    - sudo chmod 777 dmr
    - sudo apt-get update
    - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    - sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    - sudo apt-get update
    - sudo apt-get install docker-ce docker-ce-cli containerd.io
    - exit
Step 4: Deploy ILS
    - add <EC2_URL> and <EC2_URL>:8001 to the ALLOWED_HOSTS list in the settings.py file of the ILS
    - delete the venv, __pycache__, and .idea folders from your local ILS directory, along with any other unnecessary files (e.g. .coveragerc)
    - sudo scp -i ~/Downloads/ec2key.pem -r ~/amos-pj-ws20-21-computer-vision-for-sights/amos/image_labelling_service  ubuntu@<EC2_URL>:~/ils/
    - sudo ssh -i ~/Downloads/ec2key.pem ubuntu@<EC2_IP>
    - cd ils/image_labelling_service
    - sudo docker build -t ils .
    - sudo docker run -d -e PGHOST=<PGHOST> -e PGDATABASE=<PG_DATABASE> -e PGUSER=<PG_USER> -e PGPORT=<PG_PORT> -e PGPASSWORD=<PG_PASSWORD> -e MAX_GOOGLE_VISION_CALLS_PER_NEW_CITY=<MAX_GOOGLE_VISION_CALLS_PER_NEW_CITY> -p 8001:8001 -it ils
Step 5: Deploy DOS
    - add <EC2_URL> and <EC2_URL>:8002 to the ALLOWED_HOSTS list in the settings.py file of the DOS
    - delete the venv, __pycache__, and .idea folders from your local DOS directory, along with any other unnecessary files (e.g. .coveragerc)
    - sudo scp -i ~/Downloads/ec2key.pem -r ~/amos-pj-ws20-21-computer-vision-for-sights/amos/django_orchestrator  ubuntu@<EC2_URL>:~/dos/
    - sudo ssh -i ~/Downloads/ec2key.pem ubuntu@<EC2_IP>
    - cd dos/django_orchestrator
    - sudo docker build -t dos .
    - sudo docker run  -d -e PGHOST=<PGHOST> -e PGDATABASE=<PG_DATABASE> -e PGUSER=<PG_USER> -e PGPORT=<PG_PORT> -e PGPASSWORD=<PG_PASSWORD> -p 8002:8002 -it dos
Step 6: Deploy DMR (attention - by linking the DMR with the ILS, costs may arise)
    - delete the venv, __pycache__, and .idea folders from your local DMR directory, along with any other unnecessary files (e.g. .coveragerc)
    - sudo scp -i ~/Downloads/ec2key.pem -r ~/amos-pj-ws20-21-computer-vision-for-sights/amos/data_mart_refresher  ubuntu@<EC2_URL>:~/dmr/
    - sudo ssh -i ~/Downloads/ec2key.pem ubuntu@<EC2_IP>
    - cd dmr/data_mart_refresher
    - sudo docker build -t dmr .
    - sudo docker run -d -e DATA_MART_MTS_ENDPOINT_URL=<MTS_URL> -e DATA_MART_ILS_ENDPOINT_URL=http://<EC2_URL>:8001 -e DATA_MART_REFRESH_DATA_MARTS_EVERY_SECONDS=5 -e DATA_MART_ENABLE_MODEL_TRAINING_EVERY_SECONDS=10 -e DATA_MART_ENABLE_LABELLING_REQUESTS_EVERY_SECONDS=10 -e PGHOST=<PGHOST> -e PGDATABASE=<PG_DATABASE> -e PGUSER=<PG_USER> -e PGPORT=<PG_PORT> -e PGPASSWORD=<PG_PASSWORD> -it dmr
    