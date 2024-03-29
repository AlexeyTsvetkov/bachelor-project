import sys
import os
from random import shuffle
from classifiers.utils import read_labelled_set, save_classifier


def measures(label, test_set, result_set):
    tp, tn, fp, fn = 0., 0., 0., 0.

    for i in xrange(len(test_set)):
        expected = test_set[i]
        observed = result_set[i]

        if expected == label:
            if observed == label:
                tp += 1
            else:
                fn += 1
        else:
            if observed == label:
                fp += 1
            else:
                tn += 1

    precision = tp / (tp + fp + 1.)
    recall = tp / (tp + fn + 1.)
    if abs(precision + recall) <= sys.float_info.epsilon:
        f1 = 0.0
    else:
        f1 = 2. * precision * recall / (precision + recall)

    return precision, recall, f1


def cross_validation(classifier, input_set, classes, show_progress=True):
    class_count = len(classes)
    tenth = len(input_set) / 10

    p_avg, r_avg, f1_avg = 0., 0., 0.
    for i in xrange(10):
        start, end = i * tenth, (i + 1) * tenth
        train_set = input_set[:start] + input_set[end:]
        test_set = input_set[start:end]

        train_documents, train_labels = map(list, zip(*train_set))
        classifier.learn(train_documents, train_labels)

        test_documents, test_labels = map(list, zip(*test_set))
        result_labels = classifier.classify_batch(test_documents, True)

        p_whole, r_whole, f1_whole = 0., 0., 0.
        for Class in classes:
            p, r, f1 = measures(Class, test_labels, result_labels)
            p_whole += p
            r_whole += r
            f1_whole += f1

        if show_progress:
            print 'Results of iteration %i (average of all classes): %f (precision), %f (recall), %f (f1)' % \
                  (i, p_whole / class_count, r_whole / class_count, f1_whole / class_count)

        p_avg += p_whole / class_count
        r_avg += r_whole / class_count
        f1_avg += f1_whole / class_count

    return p_avg / 10., r_avg / 10., f1_avg / 10.


if __name__ == '__main__':
    from classifiers.classifier import *
    from classifiers.preprocessors import *
    from classifiers.feature_extractors import *
    from classifiers.feature_selectors import *
    from classifiers.train_classifier import get_args_parser, build_classifier_from_args

    def main():
        parser = get_args_parser()

        args = parser.parse_args()
        classifier = build_classifier_from_args(args)

        docs, labels = read_labelled_set(args.input)
        input_set = zip(docs, labels)
        shuffle(input_set)
        classes = set(labels)

        print 'Testing dataset: %s' % (args.input,)
        print 'Test method: 10-fold cross-validation\n'
        print 'Classifier: %s' % (str(classifier), )

        p, r, f1 = cross_validation(classifier, input_set, classes)
        print 'After 10-fold-average'
        print 'Precision: %f, Recall: %f, F1: %f\n' % (p, r, f1)

    main()