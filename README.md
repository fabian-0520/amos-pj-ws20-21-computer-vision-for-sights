# amos-pj-ws20-21-computer-vision-for-sights

### Run locally
Prerequirements: [Pipenv](https://pipenv.readthedocs.io/)

This project contains:

* PostgresDB
* the Image Crawler
* Data Mart Refresher

To run all of the packages this locally follow the required steps:
Please be aware that you need and **.env** file with the required environment variables:
The .env file can be found in the AMOS Documentation Tab in the Google Sheet.

You will need pipenv, because it is passing the .env file into Environment variables.

Install Dependencies:

```shell
pipenv shell
pipenv install
docker-compose up
```

<br>
<br>
To run each project single handed run the docker container of each package. More Informatione can be found in the respected directories.

* /postgres
* /amos/crawler
* /amos/data_mart_refresher
