# Sightscan crawler

Either run locally (by following steps below) or in docker container (Dockerfile)

With docker: `docker run --name crawler image_name "location_here"` where the image name is the image tag 
you set for the configuration.

This only works if you also have your api keys in .env in the same directory as this README.

## AutoCrawler library
Google multiprocess image crawler (High Quality & Speed & Customizable)

### How to use

1. Install Chrome

2. pip install -r requirements.txt

3. Write relevant runtime args

4. **Run "main.py"**

5. Files will be downloaded to 'download' directory.


### Arguments

```
--skip true        Skips keyword if downloaded directory already exists. This is needed when re-downloading.

--threads 4        Number of threads to download.

--google true      Download from google.com (boolean)

--full false       Download full resolution image instead of thumbnails (slow)

--face false       Face search mode

--no_gui auto      No GUI mode. (headless mode) Acceleration for full_resolution mode, but unstable on thumbnail mode.
                   Default: "auto" - false if full=false, true if full=true
                   (can be used for docker linux system)
                   
--limit 0          Maximum count of images to download per site. (0: infinite)

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
