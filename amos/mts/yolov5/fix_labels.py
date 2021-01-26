import os

def fix_labels(classes):
    # classes is list of classes [brandenbuger_tor, siegess, ..]
    dir = '../training_data/labels'
    translation = dict()
    for file in os.listdir(dir):
        filedata = open(dir + "/" + file, 'r')
        for line in filedata:
            label_text = line.split()[0]
            index = classes.index(label_text)
            translation[label_text] = index
            # output = filedata.read().replace(label_text, str(index))
            # print(output)

    print(translation)
    for file in os.listdir(dir):
        filedata = open(dir + "/" + file, 'w')
        # To be continued: replace in files
        # overwrite files





