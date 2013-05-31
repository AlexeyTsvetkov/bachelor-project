import argparse

from classifiers.utils import save_classifier, read_labelled_set
from classifiers.preprocessors import build_combined_preprocessor
from classifiers.classifier import NaiveBayesClassifier, MaxEntClassifier, DictionaryClassifier, HierarchicalClassifier
from classifiers.feature_extractors import NgramExtractorBoolean, NgramExtractorCount
from classifiers.feature_selectors import DeltaIdfFeatureSelector, MutualInformationFeatureSelector


def train_classifier(classifier, input_file_path, output_file_path):
    docs, labels = read_labelled_set(input_file_path)

    print 'Training classifier: %s' % (str(classifier),)
    classifier.learn(docs, labels)

    print 'Trained, now saving...'
    save_classifier(output_file_path, classifier)

    print 'Trained classifier saved to: %s' % (args.output,)


def build_hierarchical():
    docs, labels = read_labelled_set('raw_data/scpn.csv')
    preprocessor = build_combined_preprocessor()
    extractor = NgramExtractorCount([1, 2])
    pos_neg = NaiveBayesClassifier(preprocessor, extractor)
    pos_neg.learn(docs, labels)

    docs, labels = read_labelled_set('raw_data/sc.csv')
    obj_subj = NaiveBayesClassifier(preprocessor, extractor)
    obj_subj.learn(docs, labels)

    result_classifier = HierarchicalClassifier(obj_subj, [(u'subjective', pos_neg)])
    save_classifier('trained_classifiers/three_class_hierarchical.obj', result_classifier)


def build_classifier_from_args(args):
    preprocessor = build_combined_preprocessor()
    if args.ngrams == 'Unigrams':
        ngrams = [1]
    elif args.ngrams == 'Bigrams':
        ngrams = [2]
    else:
        ngrams = [1, 2]

    if args.metric == 'Boolean':
        feature_extractor = NgramExtractorBoolean(ngrams)
    else:
        feature_extractor = NgramExtractorCount(ngrams)

    if args.selection:
        if args.top:
            top = args.top
        else:
            top = 0.2

        if args.selection == 'MutualInformation':
            feature_extractor = MutualInformationFeatureSelector(feature_extractor, top)
        else:
            feature_extractor = DeltaIdfFeatureSelector(feature_extractor, top)

    if args.algorithm == 'NaiveBayes':
        classifier = NaiveBayesClassifier(preprocessor, feature_extractor)
    elif args.algorithm == 'MaxEnt':
        classifier = MaxEntClassifier(preprocessor, feature_extractor)
    else:
        classifier = DictionaryClassifier(preprocessor, feature_extractor)

    return classifier

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Training a sentiment classifier')
    parser.add_argument('--algorithm', choices=['NaiveBayes', 'MaxEnt', 'Dictionary'],
                        required=True,
                        help='Algorithm to use (NaiveBayes, MaxEnt or Dictionary)')

    parser.add_argument('--ngrams', choices=['Unigrams', 'Bigrams', 'Both'],
                        required=True,
                        help='Which ngrams to use for feature extraction')

    parser.add_argument('--metric', choices=['Boolean', 'Count'],
                        required=True,
                        help='Which metric to use for feature extraction (Boolean or Count)')

    parser.add_argument('--selection', choices=['MutualInformation', 'DeltaIdf'],
                        required=False,
                        help='Feature selection algorithm (MutualInformation or DeltaIdf)')

    parser.add_argument('--top', type=float,
                        required=False,
                        help='Feature selection amount (absolute value or percent of best features to use for classification)')

    parser.add_argument('--input', type=str,
                        required=True,
                        help='Input path (training dataset)')

    parser.add_argument('--output', type=str,
                        required=True,
                        help='Output path (classifier will be saved there)')


    args = parser.parse_args()
    classifier = build_classifier_from_args(args)

    train_classifier(classifier, args.input, args.output)