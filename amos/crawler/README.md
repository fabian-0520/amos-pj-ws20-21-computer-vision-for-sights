### How to: using the SightScan crawler

1. docker build . -t crawler
2. docker run -e PGHOST=<PGHOST> -e PGDATABASE=<PGDATABASE> -e PGUSER=<PGUSER> -e PGPORT=<PGPORT> -e PGPASSWORD=<PGPASSWORD> -e MAPS_KEY=<GOOGLE_MAPS_KEY> -it crawler <CITY_TO_COLLECT_SIGHTS_FOR> --sights_limit=<MAX_NUMBER_OF_DIFFERENT_SIGHTS> --limit=<MAX_NUMBER_OF_IMAGES_PER_SIGHT>


## AutoCrawler library
Google multiprocess image crawler (High Quality & Speed & Customizable)


### (Other) optional arguments to append to run command above with --<VARIABLE_NAME>=<VARIABLE_VALUE>
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


### Full Resolution Mode
You can download full resolution image of JPG, GIF, PNG files by specifying --full true


### Data Imbalance Detection
Detects data imbalance based on number of files.
When crawling ends, the message show you what directory has under 50% of average files.
I recommend you to remove those directories and re-download.
