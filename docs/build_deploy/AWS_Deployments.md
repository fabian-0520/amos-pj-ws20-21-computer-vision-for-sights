How To: Deploying ILS, DOS, MTS, and DMR Services on AWS using EC2 (using macOS or Linux) 
========================================================================================= 

# Needed variables for deployment (to be initialized when doing the deployment)
- <ILS_DOS_DMR_EC2_IP> := IP of the running EC2 instance
- <ILS_DOS_DMR_EC2_URL> := URL of the running EC2 instance (always in the form "ec2-xxx-xxx-xxx-xxx.eu-central-1.compute.amazonaws.com", where xxx-xxx-xxx-xxx is the corresponding IP address)
- <PG_HOST> := DWH host
- <PG_DATABASE> := DWH database
- <PG_USER> := DWH user
- <PG_PORT> := DWH port
- <PG_PASSWORD> := DWH password
- <MAX_GOOGLE_VISION_CALLS_PER_NEW_CITY> := max. number of allowed Vision API calls for each new supported city that has yet no labels in the DWH
- <ILS_PUBLIC_ENDPOINT_URL>: Image Labelling Service (ILS) endpoint URL for retrieving labels
- <MTS_EC2_INSTANCE_ID>: instance ID of the MTS EC2 instance
- <MTS_EC2_IP>: initial IP of the MTS EC2 instance right after deployment (changes over time)
- <MTS_EC2_URL>: initial URL of the MTS EC2 instance right after deployment (changes over time)
- <AWS_ACCESS_KEY_ID>: ID of AWS access key (needed for MTS access)
- <AWS_ACCESS_KEY>: AWS access key (needed for MTS access)
- <AWS_REGION>: AWS region (e.g. eu-central-1)
- <IS_MTS_GPU_ENABLED>: whether the deployed MTS has GPU access
- <MIN_LABELLED_IMAGES_NEEDED_FOR_TRAINING>: minimum number of labelled images needed to trigger training
- <DATA_MART_REFRESH_DATA_MARTS_EVERY_SECONDS>: frequency for refreshing DWH data marts => set at least to 60 since refreshing is computationally intensive!
- <DATA_MART_ENABLE_MODEL_TRAINING_EVERY_SECONDS>: frequency for triggering model trainings => set at least to 300 since training needs time!
- <DATA_MART_ENABLE_LABELLING_REQUESTS_EVERY_SECONDS>: frequency for retrieving image labels

# Major step #1: Deploy DWH

# Major step #2: Generate a global deployment SSH key on AWS to be reused for all components

# Major step #3: Deploy IC

# Major step #4: Deploy MTS

Step 0: Set up an EC2 instance (at least P3) for the MTS that meets the following four criteria
    1.) AMI running Ubuntu, NVidia Docker, CUDA, and PyTorch optimization, EBS as root device type for durable storage
        => e.g. "Deep Learning Base AMI (Ubuntu 18.04) Version 32.0 - ami-0d2d39cbe726f9230"
    2.) >= 80GiB of EBS storage allocated
    3.) at least one NVidia Volta GPU is assigned to the EC2 instance
    4.) auto-assign for public IP enabled
Step 1: Place your global SSH key for accessing the EC2 instance in your Downloads folder and rename it to ec2key.pem
Step 2: Prepare MTS folder structures and libraries through SSH
    - sudo ssh -i ~/Downloads/ec2key.pem ubuntu@<MTS_EC2_IP>
    - sudo mkdir mts
    - sudo chmod 777 mts
    - sudo apt-get update
    - sudo apt-get install awscli
    - exit
Step 3: Deploy MTS
    - delete venv and caches
    - sudo scp -i ~/Downloads/ec2key.pem -r ~/amos-pj-ws20-21-computer-vision-for-sights/amos/mts ubuntu@<MTS_EC2_URL>:~/mts/
    - sudo scp -i ~/Downloads/ec2key.pem ~/amos-pj-ws20-21-computer-vision-for-sights/amos/mts.sh ubuntu@<MTS_EC2_URL>:~/mts/
    - sudo ssh -i ~/Downloads/ec2key.pem ubuntu@<MTS_EC2_IP>
    - cd mts
    - command chmod +x mts.sh
    - cd mts/yolov5
    - sudo docker build -t mts .
Step 4: Wait until the DMR calls the MTS later on!

# Major step #5: Deploy DOS, ILS, and DMR

Step 1: Launch an EC2 instance for the DMR, ILS, and DMR components 
    Requirements: 
        1.) running Ubuntu
        2.) 8GB of RAM (otherwise, Docker problems may arise)
        3.) security group allows custom TCP traffic on ports 8001, 8002 from 0.0.0.0/0 and ::/0 (anywhere)
            ![Alt text](https://i.ibb.co/xjZ6wtc/Screenshot-2021-01-12-at-16-55-30.png)    
Step 2: Place your global SSH key for accessing the EC2 instance in your Downloads folder and rename it to "ec2key.pem"
Step 3: Prepare folder structures and install Docker on EC2 instance through SSH
    - sudo ssh -i ~/Downloads/ec2key.pem ubuntu@<ILS_DOS_DMR_EC2_IP>
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
    - add <ILS_DOS_DMR_EC2_URL> and <ILS_DOS_DMR_EC2_URL>:8001 to the ALLOWED_HOSTS list in the settings.py file of the ILS
    - delete the venv, __pycache__, and .idea folders from your local ILS directory, along with any other unnecessary files (e.g. .coveragerc)
    - sudo scp -i ~/Downloads/ec2key.pem -r ~/amos-pj-ws20-21-computer-vision-for-sights/amos/image_labelling_service ubuntu@<ILS_DOS_DMR_EC2_URL>:~/ils/
    - sudo ssh -i ~/Downloads/ec2key.pem ubuntu@<ILS_DOS_DMR_EC2_IP>
    - cd ils/image_labelling_service
    - sudo docker build -t ils .
    - sudo docker run -d -e PGHOST=<PGHOST> -e PGDATABASE=<PG_DATABASE> -e PGUSER=<PG_USER> -e PGPORT=<PG_PORT> -e PGPASSWORD=<PG_PASSWORD> -e MAX_GOOGLE_VISION_CALLS_PER_NEW_CITY=<MAX_GOOGLE_VISION_CALLS_PER_NEW_CITY> -p 8001:8001 -it ils
Step 5: Deploy DOS
    - add <ILS_DOS_DMR_EC2_URL> and <ILS_DOS_DMR_EC2_URL>:8002 to the ALLOWED_HOSTS list in the settings.py file of the DOS
    - delete the venv, __pycache__, and .idea folders from your local DOS directory, along with any other unnecessary files (e.g. .coveragerc)
    - sudo scp -i ~/Downloads/ec2key.pem -r ~/amos-pj-ws20-21-computer-vision-for-sights/amos/django_orchestrator ubuntu@<ILS_DOS_DMR_EC2_URL>:~/dos/
    - sudo ssh -i ~/Downloads/ec2key.pem ubuntu@<ILS_DOS_DMR_EC2_IP>
    - cd dos/django_orchestrator
    - sudo docker build -t dos .
    - sudo docker run  -d -e PGHOST=<PGHOST> -e PGDATABASE=<PG_DATABASE> -e PGUSER=<PG_USER> -e PGPORT=<PG_PORT> -e PGPASSWORD=<PG_PASSWORD> -p 8002:8002 -it dos
Step 6: Deploy DMR (attention - by linking the DMR with the ILS & MTS, costs may arise)
    - delete the venv, __pycache__, and .idea folders from your local DMR directory, along with any other unnecessary files (e.g. .coveragerc)
    - sudo scp -i ~/Downloads/ec2key.pem -r ~/amos-pj-ws20-21-computer-vision-for-sights/amos/data_mart_refresher ubuntu@<ILS_DOS_DMR_EC2_URL>:~/dmr/
    - sudo ssh -i ~/Downloads/ec2key.pem ubuntu@<ILS_DOS_DMR_EC2_IP>
    - cd dmr/data_mart_refresher
    - sudo docker build -t dmr .
    - sudo docker run -d -e ILS_PUBLIC_ENDPOINT_URL=<ILS_PUBLIC_ENDPOINT_URL> -e MTS_EC2_INSTANCE_ID=<MTS_EC2_INSTANCE_ID> -e AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID> -e AWS_ACCESS_KEY=<AWS_ACCESS_KEY> -e AWS_REGION=<AWS_REGION> -e IS_MTS_GPU_ENABLED=<False | True> -e DATA_MART_REFRESH_DATA_MARTS_EVERY_SECONDS=<DATA_MART_REFRESH_DATA_MARTS_EVERY_SECONDS> -e DATA_MART_ENABLE_MODEL_TRAINING_EVERY_SECONDS=<DATA_MART_ENABLE_MODEL_TRAINING_EVERY_SECONDS> -e DATA_MART_ENABLE_LABELLING_REQUESTS_EVERY_SECONDS=<DATA_MART_ENABLE_LABELLING_REQUESTS_EVERY_SECONDS> -e PGHOST=<PGHOST> -e PGDATABASE=<PGDATABASE> -e PGUSER=<PGUSER> -e PGPORT=<PGPORT> -e PGPASSWORD=<PGPASSWORD> -it data_mart_refresher
    