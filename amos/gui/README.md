## SightScan Desktop-App
Load images and detect sights in the SightScan Desktop app.

### How to start
1. "pip install -r requirements.txt"

2. Add the .env file to the gui/dwh_communication folder. This file should specify host, port, database, user and password of our AWS DWH.

3. "python main.py" or double-click the main.py


### How to use - current functionalities are all optional
- select your city in the top-left corner and confirm the selection, which later should trigger the download of the specific pretrained model
- enable / disable loading of images in the bottom-left corner
- when loading images is enabled, load images by dragging and dropping them into the target in the application
- detection button in the bottom-right corner currently outputs the path of the image loaded into the application

### Future work
- button to request the addition of a new city
- enabling client-side image labelling
- download the specific pretrained model associated with the currently selected city
- if nothing was detected - ask for support by the user by labeling the current image or by telling the application which sight is in the image --> create new class for the sight ???
- what to do with incorrect use of the application, e.g. labeling an image with no sight in it - confusing the model...
	e.g. request for adding a new city with irregular name / too small, too uninsteresting
	e.g. loading non-image files --> label should still display "Drop the image here"
