# Sightscan crawler

Either run locally (by following steps below) or in docker container (Dockerfile)

With docker: `docker run --name crawler image_name "['keyword','list','here']"` where the image name is the image tag 
you set for the configuration.

## AutoCrawler library
Google multiprocess image crawler (High Quality & Speed & Customizable)

### How to use

1. Install Chrome

2. pip install -r requirements.txt

3. Write search keywords in keywords.txt

4. **Run "main.py"**

5. Files will be downloaded to 'download' directory.


### Arguments
usage:
```
python3 main.py [--skip true] [--threads 4] [--google true] [--naver true] [--full false] [--face false] [--no_gui auto] [--limit 0]
```

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

--keyword_list ['Brandenburger Tor'] The list of keyowrds that the crawler will extract.
```


### Full Resolution Mode

You can download full resolution image of JPG, GIF, PNG files by specifying --full true


### Data Imbalance Detection

Detects data imbalance based on number of files.

When crawling ends, the message show you what directory has under 50% of average files.

I recommend you to remove those directories and re-download.
