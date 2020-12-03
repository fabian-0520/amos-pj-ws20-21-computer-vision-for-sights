import io
import os
import  numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
from google.cloud import vision

image_path = 'input-images'


def demo():
    label_images(image_path)


def get_location(input_image):
    result = []
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=input_image)

    response = client.landmark_detection(image=image)
    labels = response.landmark_annotations

    for label in labels:
        result.append([label.bounding_poly.vertices[0].x, label.bounding_poly.vertices[0].y, label.bounding_poly.vertices[2].x, label.bounding_poly.vertices[2].y, label.description])

    return result


def visualize(path, loc, show = False):
    img = mpimg.imread(path)
    fig, ax = plt.subplots(1)
    ax.imshow(img)
    # Create a Rectangle patch
    for l in loc:
        rect = patches.Rectangle((l[0], l[3]), l[2] - l[0], l[1] - l[3], linewidth=1,
                                 edgecolor='g', facecolor='none')
        ax.add_patch(rect)
        plt.text(l[0], l[1], l[4])

    if show:
        plt.show()

    # save as file:
    plt.savefig('input-images/labelled-images/' + os.path.split(path)[len(os.path.split(path)) - 1])
    plt.close()
    print('saved: ' + 'input-images/labelled-images/' + os.path.split(path)[len(os.path.split(path)) - 1])


def export_labels(loc, image_file_name):
    output = open(image_path + '/labelled-images/' + image_file_name + '.txt', 'a')
    output.write('{')
    for j in range(len(loc)):
        sight = loc[j]
        output.write('"(')
        for i in range(len(sight)):
            value = sight[i]
            output.write(str(value))
            if i < len(sight) - 1:
                output.write(', ')
        output.write(')"')
        if j < len(loc) - 1:
            output.write(', ')
    output.write('}')


def label_images(path):
    for image in os.listdir(path):
        if image.endswith(".jpg") or image.endswith(".png") or image.endswith(".jpeg"):
            img_path = os.path.join(path, image)
            with io.open(img_path, 'rb') as image_file:
                content = image_file.read()
            loc = get_location(content)
            visualize(img_path, loc)
            export_labels(loc, image)


if __name__ == "__main__":
    demo()



