import numpy as np
import math


class ClassifierBase(object):
    def __init__(self, preprocessor, feature_extractor):
        self.preprocessor = preprocessor
        self.feature_extractor = feature_extractor
        self.classes = []

    def __str__(self):
        return 'BaseClassifier'

    def get_encoded_labels(self, labels):
        """Encodes each label to unique index in 0..unique_class_count"""

        self.class_index = {}
        self.classes = []
        self.class_probability = []

        encoded_labels = np.zeros((len(labels),))
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

    def classify_batch(self, text_set, original_class=False):
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
        """
        Fields:

        class_index -- dict, maps class (string or number) to range [0, class_count)
        classes -- list, stores original class lengths
        class_probability -- list, prior probability of particular class in test set
            (number of documents per class / total number of documents)
        features_counts -- matrix, class_count x number_of_features (vocabulary length)
            stores counts of each feature per class
        class_feature_sum -- sum of feature counts per class
        """
        super(MultinomialNaiveBayes, self).__init__(preprocessor, feature_extractor)

        self.class_index = {}
        self.classes = []
        self.class_probability = []
        self.alpha = alpha

    def __str__(self):
        return 'Algorithm=MultinomialNaiveBayes, %s' % \
               (str(self.feature_extractor),)

    def get_class_count(self):
        return len(self.classes)

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

        self.class_probability = self.get_class_prob(labels)

        self.feature_extractor.learn(documents, labels)
        self.feature_count = self.feature_extractor.features_count()

        self.features_counts = np.zeros((self.get_class_count(), self.feature_count))
        self.class_feature_sum = []

        for i in xrange(len(documents)):
            document = documents[i]
            Class = labels[i]
            feature_vector = self.feature_extractor.extract(document)
            self.features_counts[Class] += feature_vector

        for Class in xrange(self.get_class_count()):
            self.class_feature_sum.append(np.sum(self.features_counts[Class]))

    def conditional_probability(self, Class, document):
        """Probability that document belongs to Class"""
        feature_vector = self.feature_extractor.extract(document)
        prior = math.log(self.class_probability[Class], 10)
        likelihood = (self.features_counts[Class] + self.alpha) / \
                     (self.features_counts[Class] + self.feature_count * self.alpha)
        log_likelihood = np.sum(feature_vector * np.log10(likelihood))
        posterior = prior + log_likelihood
        return posterior