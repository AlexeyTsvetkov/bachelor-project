import numpy as np
import math
import random


class ClassifierBase(object):
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

    def learn(self, train_set, classes):
        """Learns from train_set
        train_set -- list of documents
        classes -- list of classes of corresponding documents
        both vectors must have equal lengths
        """
        raise NotImplementedError('ClassifierBase.learn')

    def conditional_probability(self, Class, document):
        """Probability that document belongs to Class"""
        raise NotImplementedError('ClassifierBase.conditional_probability')

    def classify_one(self, document):
        document = self.preprocessor.preprocess(document)
        classes = range(len(self.classes))
        prob_of_class = lambda c: self.conditional_probability(c, document)

        return max(classes, key=prob_of_class)

    def classify_batch(self, text_set, original_class=True):
        """Classifies each text document in text_set
        returns list of classes
        """
        result_classes = []
        for text in text_set:
            if original_class:
                result_classes.append(self.classes[self.classify_one(text)])
            else:
                result_classes.append(self.classify_one(text))
        return result_classes


class MultinomialNaiveBayes(ClassifierBase):
    def __init__(self, preprocessor, feature_extractor, alpha=1.):
        super(MultinomialNaiveBayes, self).__init__(preprocessor, feature_extractor)
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


class MaxEnt(ClassifierBase):
    def __init__(self, preprocessor, feature_extractor, epsilon=0.001):
        super(MaxEnt, self).__init__(preprocessor, feature_extractor)
        self.name = 'MaxEnt'
        self.epsilon = epsilon

    def init_weights(self, class_count, feature_count):
        weights = np.zeros((class_count, feature_count))


        return weights

    def learn(self, documents, labels):
        documents = map(self.preprocessor.preprocess, documents)
        labels = self.get_encoded_labels(labels)
        self.feature_extractor.learn(documents, labels)

        class_count = len(self.classes)
        classes = range(class_count)

        feature_count = self.feature_extractor.features_count()
        empirical_count = np.zeros((class_count, feature_count))
        feature_vectors = map(lambda doc: self.feature_extractor.extract(doc), documents)
        self.weights = self.init_weights(class_count, feature_count)
        step = 0.01

        for i in xrange(len(documents)):
            empirical_count[labels[i]] += feature_vectors[i]

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
                    delta += part_derivative ** 2

            self.weights = temp_weights
            delta = math.sqrt(delta)
            print delta
            if delta <= self.epsilon:
                break

    def conditional_probability(self, Class, document):
        feature_vector = self.feature_extractor.extract(document)
        classes = range(len(self.classes))

        probability = math.exp(np.sum(self.weights[Class] * feature_vector))
        normalizer = sum(map(lambda c: math.exp(sum(self.weights[c] * feature_vector)), classes))
        return probability / normalizer