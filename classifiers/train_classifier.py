from classifiers.common_util import read_labelled_set


def train_classifier(classifier, input_file_path, output_file_path):
    input_set = read_labelled_set(input_file_path)
    classifier.train(input_set)
    classifier.save(output_file_path)