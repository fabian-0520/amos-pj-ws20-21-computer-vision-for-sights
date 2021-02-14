## SightScan Desktop-App
Load images and detect sights in the SightScan Desktop app.

### How to start
1. "pip install -r requirements.txt"

2. Add the .env file to the gui/dwh_communication folder. This file should specify host, port, database, user and password of our AWS DWH.

3. "python main.py" or double-click the main.py


### How to use 

## City download
- select city in the top-left corner and confirm the new download or update

## Detection in image
- enable / disable loading of images by clicking button in bottom-left corner
- when loading images is enabled, load images by dragging and dropping them into the target area
- start detection by clicking on start detection button in bottom right corner

## Detection in webcam feed 
- select webcam in the top right corner
- webcam feed in displayed in application
- start detection by clicking on start detection button in bottom right corner

## Request city
- enter text at top for new city not shown in drop-down-menu
- send request by clicking add city button
- city will appear in drop-down-menu as soon as it is available

## Features
- help improve detection by checking box in top left corner -> dropped images will be used by SightScan
- debug mode by checking box in botton right corner -> added logging display, exact bounding boxes after detection and detection probability displayed
