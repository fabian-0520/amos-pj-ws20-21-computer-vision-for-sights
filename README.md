# SightScan

<img src="/amos/gui/logo.png" align="left"
width="200" hspace="10" vspace="10">

For detecting sights in _your_ city.

SightScan was completed as part of the AMOS Module in WS20/21 by Team 2 (Computer vision for sights) at the Technical University of Berlin.

## About

SightScan is an extensive architecture containing several important functions with the core idea being a 
sight/attraction detection service for cities.

SightScan allows users to download models for their own respective cities and get useful information about what his 
or her application is currently seeing.

This repository includes each step of the pipeline responsible for delivering a trained sight detection model to the end user, 
as well as a graphical user interface to detect and suggest new sights.

## Features

This repository includes:
- A model training service including a dockerfile with a corresponding wrapper responsible for storing models and fetching training data
- A modified image crawler which uses google images as a source and also fetches the top n sights for a city 
- A data mart refresher which dynamically listens to database updates and accordingly triggers relevant microservices
- A django orchestrator which is acting as a connection point to users and a starting/ending point for the training pipeline
- A gui application written in python, with the ability to detect sights, suggest cities and upload new images 
  to extend the training set
- An image labeling service responsible for adding labels to crawled images with the help of Google's Vision API
- A data warehouse integration which is adjusted perfectly for dynamic scaling and parallelisation of the entire architecture as well as the training pipeline

## Screenshots

<p float="left">
  <img src="/screenshots/gui1.png" width="400" />
  <img src="/screenshots/gui2.png" width="400" /> 
</p>

## Getting started

This project contains a detailed user documentation and build/deploy documentation inside the wiki of the repository.

Please be aware that you need an **.env** file with a set of required variables and keys.
The .env file can be found in the AMOS Documentation Tab in the Google Sheet.

You will need pipenv, because it is passing the .env file into Environment variables.

Further information can also be found in the respective directories of the services, each one containing a specific README. 
In general, the core of the application is built upon docker and docker-compose.


## Main APIs, libraries and frameworks used

Aside from python and its packages, SightScan uses several other frameworks and libraries. Here are the main ones:
- Google Vision API
- Google Places API
- PyTorch
- Docker
- AWS
- PyQT5

For a complete tech stack, please look into the technical documentation inside the wiki of this repository.

## Contributing

SightScan is open source and you are welcome to contribute and support, here are a few ways:
 * [Report bugs, make suggestions and new ideas](https://github.com/fabian-0520/amos-pj-ws20-21-computer-vision-for-sights/issues)
 * Write your own features or submit code changes in a forked version of the repository

## License

MIT
