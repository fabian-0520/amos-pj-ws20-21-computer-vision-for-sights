# USER DOCUMENTATION               
                                        
## SightScan | AMOS Project Team 2      

___________________________
### Introduction

SightScan is a personal digital sightseeing guide for any city. The application provides information about the name and location of all sights surrounding the user. The sights can either be detected on an image – manually added to the application by the user – or on a live camera feed of the user’s environment captured by a currently connected webcam.


### Getting started

Before the detection can be started, SightScan needs to download all necessary data for the city in which the sights are to be detected. In the drop-down-menu *Choose City* in the upper left corner the user can choose from all cities that are currently supported. The list is dynamically updated and always contains the most recent list of supported cities. Upon choosing SightScan checks whether the city is already available on the user’s device and gives according feedback via a pop-up-window.

1. Click  **Choose City**
2. Choose City from drop-down-menu
3. Click  **OK** in pop-up-window

![alt text](https://i.ibb.co/ftfk4cb/user-doc1.png) 

* If the city has never been downloaded before, the user is asked if they want to download the city data. The download starts after clicking **OK**.

![alt text](https://i.ibb.co/wp3BMdL/user-doc2.png)

* If there is an outdated version available, the user is asked if they want to download the updated city data. The detection will still work as before without updating. The download starts after clicking **OK**.

![alt text](https://i.ibb.co/Dg9FsdM/user-doc3.png)

* If the most recent version is available, the detection can start right away.

![alt text](https://i.ibb.co/HnbThnR/user-doc4.png)


### Detection on an image

Images can be added to SightScan via Drag-and-Drop. This function is enabled by clicking **Enable File Drop**. Now an image saved on the device can be dragged into the marked area on the application. New images can be dragged on top of the one currently displayed. Drag-and-Drop can be disabled by clicking **Disable File Drop**. Before dragging in a new image, the function needs to be enabled again.

1. Click **Enable File Drop**
2. Drag image into marked area

![alt text](https://i.ibb.co/1MGLzgM/user-doc5.png)
![alt text](https://i.ibb.co/RzWb3rw/user-doc6.png)


### Detection via Webcam

In the drop-down-menu *Choose Webcam* in the upper right corner the user can choose from all webcams that are currently connected to the device. Upon choosing the live webcam feed is started and displayed in the application. The webcam feed can be stopped by choosing the option Choose Webcam in the drop-down-menu or by enabling the image-drop.  

1. Click **Choose Webcam**
2. Choose Webcam from dropdown-menu

![alt text](https://i.ibb.co/z4Bz8Hq/user-doc7.png)


### Sight Detection

As soon as the user has dragged an image into SightScan the detection can be started by clicking **Start Detection**. It can take a moment for SightScan to detect all sights. The location – indicated by a colored dot – and name of the sights will be shown to the user. When using the webcam feed the detection is live and adapts to changes of the user’s position in real time.

1. Click **Start Detection**

![alt text](https://i.ibb.co/FhCtrBH/user-doc8.png)


### New city support

The user has the option to request the support of new cities that are not yet included in the drop-down-menu. SightScan provides a text-field for the user to enter a request. The request can be submitted by clicking **Add City** and will be processed shortly. As soon as the detection data for the requested city is available for download it will show up in the drop-down-menu. 

1. Enter city request
2. Click **Add City**
3. Click **OK**

![alt text](https://i.ibb.co/d4Zydp5/user-doc9.png)
![alt text](https://i.ibb.co/XLR24T8/user-doc10.png)

### More features

* The user can help SightScan improve. By checking the box *Help improve SightScan’s detection quality* in the upper left corner the user allows SightScan to use all uploaded images for detection refinements. 

* SightScan provides a debug mode. It can be enabled by checking the box *Debug* in the lower left corner. In debug mode the user can have insights into the logging process and receives more information about the detection. After starting the detection, the sight’s location will no longer be indicated by a dot but by its exact bounding box. Additionally, the detection probability of the sight is displayed. 

![alt text](https://i.ibb.co/Cv5xP2B/user-doc11.png)


Berlin, December 2020 | AMOS@TU Berlin in cooperation with IAV GmbH 

