import numpy as np
import math


class ClassifierBase(object):
    def __init__(self, preprocessor, feature_extractor):
        self.preprocessor = preprocessor
        self.feature_extractor = feature_extractor
        self.classes = []

    def __str__(self):
        return 'BaseClassifier'

    def learn(self, train_set, classes):
        """Learns from train_set
        train_set -- list of documents
        classes -- list of classes of corresponding documents
        both vectors must have equal lengths
        """
        raise NotImplementedError('ClassifierBase.learn')

    def classify_one(self, text):
        """Classifies text document
        returns document class
        """
        raise NotImplementedError('ClassifierBase.classify')

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
        return 'Algorithm=MultinomialNaiveBayes, FeatureExtractor=%s' % \
               (str(self.feature_extractor),)

    def get_class_count(self):
        return len(self.classes)

    def get_encoded_labels(self, labels):
        """Encodes each label to unique index in 0..unique_class_count"""

        self.class_index = {}
        self.classes = []
        self.class_probability = []

        encoded_labels = []
        class_document_count = []
        document_count = len(labels)
        for c in labels:
            if c not in self.class_index:
                self.class_index[c] = self.get_class_count()
                class_document_count.append(0)
                self.classes.append(c)
            class_document_count[self.class_index[c]] += 1
            encoded_labels.append(self.class_index[c])

        for Class in xrange(self.get_class_count()):
            self.class_probability.append(1.0 * class_document_count[Class] / document_count)

        return encoded_labels

    def learn(self, documents, labels):
        documents = map(self.preprocessor.preprocess, documents)
        labels = self.get_encoded_labels(labels)

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

    def classify_one(self, document):
        result_class = -1
        max_posterior = None
        alpha = self.alpha

        document = self.preprocessor.preprocess(document)
        feature_vector = self.feature_extractor.extract(document)
        for Class in xrange(self.get_class_count()):
            prior = math.log(self.class_probability[Class], 10)
            likelihood = (self.features_counts[Class] + alpha) /\
                         (self.features_counts[Class] + self.feature_count * alpha)
            log_likelihood = np.sum(feature_vector * np.log10(likelihood))
            posterior = prior + log_likelihood
            if not max_posterior or posterior >= max_posterior:
                result_class = Class
                max_posterior = posterior

        if result_class == -1:
            raise RuntimeError('Result class is negative for text "%s"'
                               % (document,))

        return result_class