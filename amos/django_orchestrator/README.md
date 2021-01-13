How to: run/deploy the service via Docker
_________________________________________

1. Open the terminal
2. Move into the project directory (.../django_orchestrator)
3. Build the Docker image: docker build -t django_orchestrator .
4. Run the Docker image:
docker run  -e PG_HOST=<HOST>
            -e PG_DATABASE=<DATABASE>
            -e PG_USER=<USER>
            -e PG_PORT=<PORT>
            -e PG_PASSWORD=<PASSWORD>
            -p 8002:8002
            -it django_orchestrator
5. Refer to 0.0.0.0:8002/swagger to get a nicely formatted overview of the supported communication protocol
