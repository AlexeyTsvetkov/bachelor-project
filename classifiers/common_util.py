import pickle
from classifiers import unicode_csv


def read_labelled_set(input_file_path):
    labelled_set = []

    with open(input_file_path, 'rt') as f_in:
        reader = unicode_csv.UnicodeReader(f_in)

        for row in reader:
            message = row[1]
            label = row[2]

            labelled_set.append((message, label))

    return labelled_set


def save_classifier(path, classifier):
    with open(path, 'wb') as f:
        pickle.dump(classifier, f)


def load_classifier(path):
    with open(path, 'rb') as f:
        classifier = pickle.load(f)
    return classifier