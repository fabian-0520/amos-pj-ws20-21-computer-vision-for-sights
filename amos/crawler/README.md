# SightScan: Image Crawler (IC) Component
=========================================

## How to: building and running the SightScan image crawler locally in a Docker container

1. docker build . -t crawler
2. docker run -e PGHOST=<PGHOST> -e PGDATABASE=<PGDATABASE> -e PGUSER=<PGUSER> -e PGPORT=<PGPORT> -e PGPASSWORD=<PGPASSWORD> -e MAPS_KEY=<GOOGLE_MAPS_KEY> -it crawler <CITY_TO_COLLECT_SIGHTS_FOR> --sights_limit=<MAX_NUMBER_OF_DIFFERENT_SIGHTS> --limit=<MAX_NUMBER_OF_IMAGES_PER_SIGHT>

## How to: running tests incl. coverage

1. Open the terminal
2. Move into the project directory (.../crawler)
3. Run: pip install -r requirements.txt
4. Run: coverage run -m pytest -v
5. Show coverage: coverage report

## AutoCrawler library
The crawler SightScan utilizes relies on the existing AutoCrawler library (see sources).

## (Other) optional command line arguments to append to run command above with --<VARIABLE_NAME>=<VARIABLE_VALUE>
```
--skip true        Skips keyword if downloaded directory already exists. This is needed when re-downloading.

--threads 4        Number of threads to download.

--google true      Download from google.com (boolean)

--full false       Download full resolution image instead of thumbnails (slow)

--face false       Face search mode

--no_gui auto      No GUI mode. (headless mode) Acceleration for full_resolution mode, but unstable on thumbnail mode.
                   Default: "auto" - false if full=false, true if full=true
                   (can be used for docker linux system)
                   
--limit 0          Maximum count of images to download per sight. (0: infinite)

--no_driver false Whether a driver should be used

--location 'Berlin' The location keywords need to be found for.

--sights_limit The limit of sights to be found by the collector api
```

## Sources
For more information, visit: https://github.com/YoongiKim/AutoCrawler
