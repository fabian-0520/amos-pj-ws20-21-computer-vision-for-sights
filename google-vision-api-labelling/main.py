import io
import os
from google.cloud import vision
import getLocation

client = vision.ImageAnnotatorClient()

file_name = os.path.relpath('input-images/image.jpg')
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

res = getLocation.getLocation(content)
print(res)

#response = client.landmark_detection(image=image)
#labels = response.landmark_annotations

#print('Labels:')
#for label in labels:
#    print(label.description)
#    for i in range(4):
#        print(label.bounding_poly.vertices[i])





