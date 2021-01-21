How to: MTS-deployment on AWS and integration of MTS with DMR
=============================================================

Requirements: 
    1.) DMR NOT deployed yet
    2.) DMR and MTS share the same global SSH key

Step 0: Set up an EC2 instance that meets the following four criteria
    a.) AMI with NVidia Docker, CUDA, and PyTorch optimization, EBS as root device type for durable storage
        => e.g. "Deep Learning Base AMI (Ubuntu 18.04) Version 32.0 - ami-0d2d39cbe726f9230"
    b.) >= 80GiB of EBS storage allocated
    c.) at least one NVidia GPU is assigned to the EC2 instance
    d.) auto-assign for public IP enabled
Step 1: Place your private SSH key for accessing the EC2 instance in your Downloads folder and rename it to ec2key.pem
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
    - sudo ssh -i ~/Downloads/ec2key.pem ubuntu@<MTS_EC2_IP>
    - cd mts/mts/yolov5
    - sudo docker build -t mts .
Step 4: Wait until the DMR calls the MTS! :) 