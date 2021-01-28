How to: run/deploy the service via Docker

---

1. Open the terminal
2. Move into the project directory (.../django_orchestrator)
3. Build the Docker image: docker build -t django_orchestrator .
4. Run the Docker image:
   docker run -e AWS_USER=<AWS_USER>
   -e CRAWLER_HOST=<CRAWLER_HOST>
   -e REGISTRY_HOST=<REGISTRY_HOST>
   -e PG_HOST=<PG_HOST>
   -e PG_DATABASE=<PG_DATABASE>
   -e PG_USER=<PG_USER>
   -e PG_PORT=<PG_PORT>
   -e PG_PASSWORD=<PG_PASSWORD>
   -e GOOGLE_API_KEY=<GOOGLE_API_KEY>
   -e GOOGLE_MAPS_KEY=<GOOGLE_MAPS_KEY>
   -p 8002:8002
   -it django_orchestrator
5. Refer to 0.0.0.0:8002/swagger to get a nicely formatted overview of the supported communication prsotocol
