import io
import os
from google.cloud import vision

def getLocation(input_image):
    result = dict()
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=input_image)

    response = client.landmark_detection(image=image)
    labels = response.landmark_annotations

    for label in labels:
        result[str(label.description)] = [label.bounding_poly.vertices[0], label.bounding_poly.vertices[1], label.bounding_poly.vertices[2], label.bounding_poly.vertices[3]]

    return  result



