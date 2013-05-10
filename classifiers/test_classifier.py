from random import shuffle
from classifiers.util import load_classifier, read_labelled_set


def measures(label, test_set, result_set):
    tp, tn, fp, fn = 0., 0., 0., 0.

    for i in xrange(len(test_set)):
        expected = test_set[i]
        observed = result_set[i]

        if expected[1] == label:
            if observed[1] == label:
                tp += 1
            else:
                fn += 1
        else:
            if observed[1] == label:
                fp += 1
            else:
                tn += 1

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * precision * recall / (precision + recall)

    return precision, recall, f1


def cross_validation(classifier, input_set):
    labels = set((row[1] for row in input_set))
    l = len(labels)
    tenth = len(input_set) / 10

    shuffle(input_set)
    p_avg, r_avg, f1_avg = 0., 0., 0.
    for i in xrange(10):
        start, end = i * tenth, (i + 1) * tenth
        train_set = input_set[:start] + input_set[end:]
        test_set = input_set[start:end]

        classifier.train(train_set)
        result_set = classifier.batch_classify(test_set)

        p_whole, r_whole, f1_whole = 0., 0., 0.
        for label in labels:
            p, r, f1 = measures(label, test_set, result_set)
            p_whole += p
            r_whole += r
            f1_whole += f1

        p_avg += p_whole / l
        r_avg += r_whole / l
        f1_avg += f1_whole / l

    return p_avg / 10., r_avg / 10., f1_avg / 10.


def test_classifier(classifier_path, input_file_path):
    classifier = load_classifier(classifier_path)
    input_set = read_labelled_set(input_file_path)

    p_avg, r_avg, f1_avg = cross_validation(classifier, input_set)
    print '''Classifier: %s
     Input set: %s
     Precision: %f
     Recall: %f
     F1: %f''' % (classifier_path, input_file_path, p_avg, r_avg, f1_avg)