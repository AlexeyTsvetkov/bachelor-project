import argparse
from classifiers.common_util import read_labelled_set
from classifiers.preprocessors import build_preprocessor


def train_classifier(classifier, input_file_path, output_file_path):
    input_set = read_labelled_set(input_file_path)
    classifier.train(input_set)
    classifier.save(output_file_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Training a sentiment classifier')
    parser.add_argument('--lowercase', action='store_true', default=False,
                        help='Do not transform text to lowercase')
    parser.add_argument('--encode-mentions', action='store_true', default=False,
                        help='Encode user mentions as USER_TOKEN')
    parser.add_argument('--encode-urls', action='store_true', default=False,
                        help='Encode urls as URL_TOKEN')
    parser.add_argument('--encode-emoticons', action='store_true', default=False,
                        help='Encode positive or negative smileys with tokens POSITIVE_SMILEY and NEGATIVE_SMILEY')
    parser.add_argument('--remove-hashtags', action='store_true', default=False,
                        help='Remove hashtags')
    parser.add_argument('--remove-lengthening', action='store_true', default=False,
                        help='Replace two or more repeating characters with two (goood to good)')
    parser.add_argument('--remove-punctuation', action='store_true', default=False,
                        help='Remove punctuation')
    parser.add_argument('--remove-whitespace', action='store_true', default=False,
                        help='Replace sequence of whitespace characters with one space')
    parser.add_argument('--all-preprocessors', action='store_true', default=False,
                        help='Use all of them')

    args = parser.parse_args()
    preprocessor = build_preprocessor(args)
    input_set = read_labelled_set('./raw_data/sanders_corpus.csv')
    for row in input_set:
        print preprocessor.preprocess(row[0])