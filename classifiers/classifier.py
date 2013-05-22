import numpy as np
import math


class ClassifierBase(object):
    def __init__(self, preprocessor, feature_extractor):
        self.preprocessor = preprocessor
        self.feature_extractor = feature_extractor

    def __repr__(self):
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

    def classify_batch(self, text_set):
        """Classifies each text document in text_set
        returns list of classes
        """
        result_classes = []
        for text in text_set:
            result_classes.append(self.classify_one(text))


class MultinomialNaiveBayes(ClassifierBase):
    def __init__(self, preprocessor, feature_extractor):
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

    def __repr__(self):
        return 'Algorithm=MultinomialNaiveBayes, FeatureExtractor=%s' % \
               (self.feature_extractor,)

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

        for Class in xrange(len(labels)):
            self.class_probability.append(1.0 * class_document_count[Class] / document_count)

        return encoded_labels

    def learn(self, train_set, classes):
        train_set = map(self.preprocessor.preprocess, train_set)
        classes = self.get_encoded_labels(classes)

        self.feature_extractor.learn(train_set, classes)
        self.feature_count = self.feature_extractor.features_count()

        self.features_counts = np.zeros((self.get_class_count(), self.feature_count))
        self.class_feature_sum = []

        for i in xrange(len(train_set)):
            text = train_set[i]
            Class = self.class_index[classes[i]]
            feature_vector = self.feature_extractor.extract(text)
            np.add(self.features_counts[Class], feature_vector)

        for Class in xrange(self.get_class_count()):
            self.class_feature_sum = np.sum(self.features_counts[Class])

    def classify_one(self, text):
        result_class = -1
        max_posterior = -1

        text = self.preprocessor.preprocess(text)
        feature_vector = self.feature_extractor.extract(text)
        for Class in xrange(self.get_class_count()):
            prior = math.log(self.class_probability[Class], 2)
            likelihood = np.sum(np.log2(feature_vector / self.class_feature_sum[Class]))
            posterior = prior + likelihood
            if posterior >= max_posterior:
                result_class = Class

        if result_class == -1:
            raise RuntimeError('Result class is negative for text "%s"' % text)

        return result_class