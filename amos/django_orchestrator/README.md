# SightScan: Django Orchestration Service (DOS) Component
=========================================================

## How to: building and running the SightScan Django orchestration service locally in a Docker container

1. Open the terminal
2. Move into the project directory (.../django_orchestrator)
3. Place the SSH key of the Image Crawler's EC2 instance is the project root directory and name it "ec2key.pem".
4. Build the Docker image: docker build -t django_orchestrator .
5. Run the Docker image:
   docker run -d
   -e PGHOST=<PGHOST>
   -e PGDATABASE=<PGDATABASE>
   -e PGUSER=<PGUSER>
   -e PGPORT=<PGPORT>
   -e PGPASSWORD=<PGPASSWORD>
   -e IC_URL=<IMAGE_CRAWLER_URL>
   -e MAX_SIGHTS_PER_CITY=<MAX_SIGHTS_PER_CITY>
   -e MAX_IMAGES_PER_SIGHT=<MAX_IMAGES_PER_SIGHT>
   -e MAPS_KEY=<GOOGLE_MAPS_KEY>
   -p <DOS_PORT>:8002
   -it django_orchestrator
6. Refer to 0.0.0.0:<DOS_PORT>/swagger to get a nicely formatted overview of the supported communication protocol

## How to: running tests incl. coverage

1. Open the terminal
2. Move into the project directory (.../django_orchestrator)
3. Run: pip install -r requirements.txt
4. Run: coverage run -m pytest -v
5. Show coverage: coverage report
