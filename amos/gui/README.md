# SightScan: Graphical User Interface Component
================================================
​
## How to: building and running the SightScan GUI on your device
​
1. Open your terminal of choice
2. Move into the project directory (.../gui)
3. "pip install -r requirements.txt"
4. Add the .env file to the gui/api_communication folder. This file should specify the API_ENDPOINT_URL of our AWS DWH.
5. Start the main.py by using "python main.py" or double-click
​
## How to: Use the SighScan GUI on your device 

### City download
- select city in the top-left corner and confirm the new download or update

### Detection in image
- enable / disable loading of images by clicking button in bottom-left corner
- when loading images is enabled, load images by dragging and dropping them into the target area
- start detection by clicking on start detection button in bottom right corner

### Detection in webcam feed 
- select webcam in the top right corner
- webcam feed in displayed in application
- start detection by clicking on start detection button in bottom right corner

### Request city
- enter text at top for new city not shown in drop-down-menu
- send request by clicking add city button
- city will appear in drop-down-menu as soon as it is available

### Features
- help improve detection by checking box in top left corner -> dropped images will be used by SightScan
- debug mode by checking box in botton right corner -> added logging display, exact bounding boxes after detection and detection probability displayed


