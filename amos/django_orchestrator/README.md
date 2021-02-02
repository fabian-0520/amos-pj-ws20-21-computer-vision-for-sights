How to: run/deploy the service via Docker

---

1. Open the terminal
2. Move into the project directory (.../django_orchestrator)
3. Build the Docker image: docker build -t django_orchestrator .
4. Run the Docker image:
   docker run -d
   -e PGHOST=<PGHOST>
   -e PGDATABASE=<PGDATABASE>
   -e PGUSER=<PGUSER>
   -e PGPORT=<PGPORT>
   -e PGPASSWORD=<PGPASSWORD>
   -e IC_URL=<IMAGE_CRAWLER_URL>
   -e MAX_SIGHTS_PER_CITY=<MAX_SIGHTS_PER_CITY>
   -e MAX_IMAGES_PER_SIGHT=<MAX_IMAGES_PER_SIGHT>
   -e GOOGLE_MAPS_KEY=<GOOGLE_MAPS_KEY>
   -p 8002:8002
   -it django_orchestrator
5. Refer to 0.0.0.0:8002/swagger to get a nicely formatted overview of the supported communication protocol
