import numpy as np
import math
import os


class BaseClassifier(object):
    def __init__(self, preprocessor, feature_extractor):
        """
        Fields:

        class_index -- dict, maps class (string or number) to range [0, class_count)
        classes -- list, stores original class lengths
        """
        self.preprocessor = preprocessor
        self.feature_extractor = feature_extractor
        self.classes = []
        self.class_index = {}
        self.name = 'ClassifierBase'

    def __str__(self):
        return 'Algorithm=%s, %s' % \
               (self.name, str(self.feature_extractor),)

    def get_encoded_labels(self, labels):
        """Encodes each label to unique index in 0..unique_class_count"""

        self.class_index = {}
        self.classes = []
        self.class_probability = []

        encoded_labels = np.zeros((len(labels),), dtype=np.int)
        for i in xrange(len(labels)):
            label = labels[i]
            if label not in self.class_index:
                self.class_index[label] = len(self.classes)
                self.classes.append(label)
            encoded_labels[i] = self.class_index[label]

        return encoded_labels

    def learn(self, documents, labels):
        """Learns from train_set
        documents -- list of documents
        labels -- list of labels of corresponding documents
        both vectors must have equal lengths
        """
        raise NotImplementedError('ClassifierBase.learn')

    def conditional_probability(self, Class, document):
        """Probability that document belongs to Class"""
        raise NotImplementedError('ClassifierBase.conditional_probability')

    def classify_one(self, document, original_class=True):
        document = self.preprocessor.preprocess(document)
        classes = range(len(self.classes))
        prob_of_class = lambda c: self.conditional_probability(c, document)

        result_class = max(classes, key=prob_of_class)
        if original_class:
            return self.classes[result_class]

        return result_class

    def classify_batch(self, text_set, original_class=True):
        """Classifies each text document in text_set
        returns list of classes
        """
        result_classes = []
        for text in text_set:
            result_classes.append(self.classify_one(text, original_class))
        return result_classes


class NaiveBayesClassifier(BaseClassifier):
    def __init__(self, preprocessor, feature_extractor, alpha=1.):
        super(NaiveBayesClassifier, self).__init__(preprocessor, feature_extractor)
        self.alpha = alpha
        self.name = 'MultinomialNaiveBayes'

    def get_class_prob(self, labels):
        class_count = len(self.classes)
        class_document_count = np.zeros(class_count)
        document_count = len(labels)

        for label in labels:
            class_document_count[label] += 1

        return class_document_count / document_count

    def learn(self, documents, labels):
        documents = map(self.preprocessor.preprocess, documents)
        labels = self.get_encoded_labels(labels)
        class_count = len(self.classes)

        self.feature_extractor.learn(documents, labels)
        self.feature_count = self.feature_extractor.features_count()

        self.class_probability = self.get_class_prob(labels)
        self.features_counts = np.zeros((class_count, self.feature_count))
        self.class_feature_sum = []

        for i in xrange(len(documents)):
            document = documents[i]
            Class = labels[i]
            feature_vector = self.feature_extractor.extract(document)
            self.features_counts[Class] += feature_vector

        for Class in xrange(class_count):
            self.class_feature_sum.append(np.sum(self.features_counts[Class]))

    def conditional_probability(self, Class, document):
        feature_vector = self.feature_extractor.extract(document)
        prior = math.log(self.class_probability[Class], 10)
        likelihood = (self.features_counts[Class] + self.alpha) / \
                     (self.features_counts[Class] + self.feature_count * self.alpha)
        log_likelihood = np.sum(feature_vector * np.log10(likelihood))
        posterior = prior + log_likelihood
        return posterior


class MaxEntClassifier(BaseClassifier):
    def __init__(self, preprocessor, feature_extractor, epsilon=0.05, num_iter=5, step=0.001):
        super(MaxEntClassifier, self).__init__(preprocessor, feature_extractor)
        self.name = 'MaxEnt'
        self.epsilon = epsilon
        self.step = step
        self.num_iter = num_iter

    def init_weights(self, class_count, feature_count):
        weights = np.zeros((class_count, feature_count))
        return weights

    def learn(self, documents, labels, show_progress=True):
        documents = map(self.preprocessor.preprocess, documents)
        labels = self.get_encoded_labels(labels)
        self.feature_extractor.learn(documents, labels)

        class_count = len(self.classes)
        classes = range(class_count)

        feature_count = self.feature_extractor.features_count()
        empirical_count = np.zeros((class_count, feature_count))
        feature_vectors = map(lambda doc: self.feature_extractor.extract(doc), documents)
        self.weights = self.init_weights(class_count, feature_count)
        step = self.step
        num_iter = self.num_iter

        for i in xrange(len(documents)):
            empirical_count[labels[i]] += feature_vectors[i]

        itr = 0
        while True:
            temp_weights = np.zeros((class_count, feature_count))
            delta = 0.0

            conditional_probability = np.zeros((len(documents), class_count))
            for i in xrange(len(documents)):
                feature_vector = feature_vectors[i]
                normalizer = sum(map(lambda c: math.exp(sum(self.weights[c] * feature_vector)), classes))
                for Class in classes:
                    conditional_probability[i][Class] = math.exp(np.sum(self.weights[Class] * feature_vector)) / normalizer

            for Class in classes:
                for Feature in xrange(feature_count):
                    predicted_count = 0.0
                    for i in xrange(len(documents)):
                        if labels[i] == Class:
                            predicted_count += feature_vectors[i][Feature] * conditional_probability[i][Class]

                    part_derivative = empirical_count[Class][Feature] - predicted_count
                    temp_weights[Class][Feature] = self.weights[Class][Feature] + step * part_derivative
                    delta += (part_derivative) ** 2

            self.weights = temp_weights
            delta = math.sqrt(delta) / (class_count * feature_count)
            if show_progress:
                print delta
            itr += 1
            if delta <= self.epsilon or (num_iter and itr >= num_iter):
                break

    def conditional_probability(self, Class, document):
        feature_vector = self.feature_extractor.extract(document)
        classes = range(len(self.classes))

        probability = math.exp(np.sum(self.weights[Class] * feature_vector))
        normalizer = sum(map(lambda c: math.exp(sum(self.weights[c] * feature_vector)), classes))
        return probability / normalizer


class DictionaryClassifier(BaseClassifier):
    def __init__(self, preprocessor, feature_extractor):
        super(DictionaryClassifier, self).__init__(preprocessor, feature_extractor)
        self.name = 'Dictionary'
        dir = os.path.dirname(os.path.realpath(__file__))
        self.positive_words = self.read_set_from_file(os.path.join(dir, 'opinion_words/positive-words.txt'))
        self.negative_words = self.read_set_from_file(os.path.join(dir, 'opinion_words/negative-words.txt'))

    def read_set_from_file(self, path):
        result = set([])
        with open(path, 'rt') as f:
            for line in f:
                result.add(line.strip())
        return result

    def learn(self, train_set, classes):
        pass

    def classify_one(self, document, original_class=True):
        document = self.preprocessor.preprocess(document)
        pos_count = 0
        neg_count = 0
        for word in document.split():
            if word in self.positive_words:
                pos_count += 1
            if word in self.negative_words:
                neg_count += 1

        if pos_count >= neg_count:
            return u'positive'
        else:
            return u'negative'

    def classify_batch(self, text_set, original_class=True):
        result = []
        for document in text_set:
            result.append(self.classify_one(document))
        return result


class HierarchicalClassifier(BaseClassifier):
    def __init__(self, classifier, pipelines):
        """ Pipelines is a list of tuples (class_name, classifier)
        if result class of first classifier equals to class_name
        then second classifier used"""
        self.name = 'HierarchicalClassifier'
        self.classifier = classifier
        self.pipelines = pipelines

    def learn(self, train_set, classes):
        pass

    def classify_one(self, document, original_class=True):
        result = self.classifier.classify_one(document)
        for Class, classifier in self.pipelines:
            if Class == result:
                return classifier.classify_one(document)
        return result