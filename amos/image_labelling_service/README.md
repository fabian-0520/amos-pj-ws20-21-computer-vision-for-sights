How to: run/deploy the service via Docker
_________________________________________

1. Open your terminal.
2. Move into the project directory (.../image_labelling_service).
3. Insert a JSON file with the exact name "auth.json" into the (currently opened) project directory.
    This file contains a single JSON object that includes the following keys:
    ["type", "project_id", "private_key_id", 
    "private_key", "client_email", 
    "client_id", "auth_uri", "token_uri", 
    "auth_provider_x509_cert_url", "client_x509_cert_url"]. 
    The individual authentication parameters must be retrieved from the created Google Cloud project, cf. https://cloud.google.com/vision/docs/setup.
4. Talk to management and get to know which number to use for the MAX_GOOGLE_VISION_CALLS_PER_NEW_CITY parameter.
- It corresponds to the maximum number of unlabelled images *PER NEW CITY* that are being labelled using the Google Vision API. 
- This parameter is only relevant for cities that DO NOT HAVE ANY IMAGE LABELS yet (= for the initial labelling phase).
5. Build the Docker image: docker build -t image_labelling_service .
6. Run the Docker image:
docker run  -e PG_HOST=<HOST>
            -e PG_DATABASE=<DATABASE>
            -e PG_USER=<USER>
            -e PG_PORT=<PORT>
            -e PG_PASSWORD=<PASSWORD>
            -e MAX_GOOGLE_VISION_CALLS_PER_NEW_CITY=<MAX_GOOGLE_VISION_CALLS_PER_NEW_CITY>
            -p 7331:7331
            -it image_labelling_service
7. Refer to 0.0.0.0:7331/swagger to get a nicely formatted overview of the supported communication protocol
