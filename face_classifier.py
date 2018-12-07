import os
import glob
from collections import OrderedDict

try:
    import cPickle as pickle
except ImportError:
    import pickle

import numpy as np
from sklearn.svm import SVC
import click


def classify(faces_output_path):
    items = os.listdir(faces_output_path)
    if len(items) == 0:
        raise Exception('no items in path')

    class_names = OrderedDict()

    face_to_descriptor_file_name = 'face_to_descriptor.pickle'
    if face_to_descriptor_file_name not in items:
        raise Exception('file \"%s\" not found' % face_to_descriptor_file_name)
    with open(os.path.join(faces_output_path, face_to_descriptor_file_name), 'rb') as infile:
        face_to_descriptor = pickle.load(infile)

    descriptors = []
    labels = []

    for item in items:
        label_folder_path = os.path.join(faces_output_path, item)
        if os.path.isdir(label_folder_path):
            label_and_name = item.split('-', 1)
            if len(label_and_name) == 2:
                face_label = int(label_and_name[0])
                class_names[face_label] = label_and_name[1]
                #
                for f in glob.glob(os.path.join(label_folder_path, '*.jpg')):
                    face_id = os.path.basename(f)[:-4]
                    if os.path.isfile(f) and len(face_id) > 0:
                        descriptors.append(np.asarray(face_to_descriptor[face_id]))
                        labels.append(face_label)

    model = SVC(kernel='linear', probability=True)
    model.fit(descriptors, labels)

    with open(os.path.join(faces_output_path, 'face_classifier.pickle'), 'wb') as outfile:
        pickle.dump((model, class_names), outfile)


@click.command()
@click.argument('faces_output_path')
def main(faces_output_path):
    if not os.path.isdir(faces_output_path):
        print('\"%s\" not exists' % faces_output_path)
        return

    classify(faces_output_path)


if __name__ == '__main__':
    main()
