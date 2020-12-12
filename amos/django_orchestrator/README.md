How to: run/deploy the service via Docker
_________________________________________

1. Open the terminal
2. Move into the project directory (.../django_orchestrator)
3. Build the Docker image: docker build -t django_orchestrator .
4. Run the Docker image:
docker run  -e PG_HOST=postgres.cxuqxclhqrjq.eu-central-1.rds.amazonaws.com
            -e PG_DATABASE=postgres
            -e PG_USER=postgres
            -e PG_PORT=5432
            -e PG_PASSWORD=dwh-sight-scan
            -p 1337:1337
            -it django_orchestrator
5. Refer to 0.0.0.0:1337/swagger to get a nicely formatted overview of the supported communication protocol
