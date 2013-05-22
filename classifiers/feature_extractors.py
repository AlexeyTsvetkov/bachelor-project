import numpy as np
import math

from classifiers import constants


class FeatureExtractorBase(object):
    def __repr__(self):
        return 'FeatureExtractorBase'

    def learn(self, text_list, sentiment_list):
        """Learns features from a training set
        sentiment_list -- vector of text_list's document sentiment"""
        raise NotImplementedError('FeatureExtractorBase:learn(self, text_list) is not defined')

    def extract(self, text):
        """Extracts feature vector from text document"""
        raise NotImplementedError('FeatureExtractorBase:extract(self, text) is not defined')


class NgramExtractorBase(FeatureExtractorBase):
    def __init__(self, ns):
        """

        ns -- array of desired ngrams sizes
            e.g ns=[1,2] extracts all unigrams and bigrams

        """

        ns.sort()
        self.ns = ns
        self.ngrams = {}
        self.feature_list = []
        self.positive_frequency = {}
        self.negative_frequency = {}
        self.positive_documents_count = 0
        self.negative_documents_count = 0
        self.name = 'NgramExtractorBase'

    def __repr__(self):
        return '%s, ngrams=[%s]' % (self.name, ', '.join(self.ns),)

    def features_count(self):
        return len(self.feature_list)

    def try_get_ngram(self, words, len_n, end_pos):
        """Extracts ngram from words list, if possible

        words -- list of words
        len_n -- length of ngram
        end_pos -- ending position of ngram
        """
        if end_pos >= len_n - 1:
            ngram = u' '.join(words[end_pos - len_n + 1:end_pos + 1:])
            return ngram
        return None

    def learn_from_one(self, words, Class):
        """Learns features from one text document (list of words)"""
        for i in xrange(len(words)):
            for n in self.ns:
                ngram = self.try_get_ngram(words, n, i)
                if ngram and ngram not in self.ngrams:
                    self.ngrams[ngram] = len(self.feature_list)
                    self.feature_list.append(ngram)
                if Class == constants.POSITIVE_CODE:
                    freq = self.positive_frequency.get(ngram, 0)
                    self.positive_frequency[ngram] = freq + 1
                else:
                    freq = self.negative_frequency.get(ngram, 0)
                    self.negative_frequency[ngram] = freq + 1

    def learn(self, documents, classes):
        """Learns features from a training set"""
        for i in xrange(len(documents)):
            text = documents[i]
            sentiment = classes[i]
            if sentiment == constants.POSITIVE_CODE:
                self.positive_documents_count += 1
            else:
                self.negative_documents_count += 1

            words = text.split()
            self.learn_from_one(words, sentiment)

    def add_ngram(self, feature_vector, ngram):
        """Adds ngram to feature vector"""
        raise NotImplementedError('NgramExtractorBase:add_ngram() is not defined')

    def extract(self, text):
        """Extracts ngrams as vector [a_1, ..., a_n] where
        n is number of features in training"""
        f_num = len(self.feature_list)
        feature_vector = np.zeros((f_num,))
        words = text.split()
        for i in xrange(len(words)):
            for n in self.ns:
                ngram = self.try_get_ngram(words, n, i)
                if ngram and ngram in self.ngrams:
                    self.add_ngram(feature_vector, ngram)
        return feature_vector


class NgramExtractorBoolean(NgramExtractorBase):
    """Values a_i of feature_vector [a_1, ..., a_n] equal
        1 if ngram_i is presented in text document
        0 otherwise
    """

    def __init__(self, ns):
        super(NgramExtractorBoolean, self).__init__(ns)
        self.name = 'NgramExtractorBoolean'

    def add_ngram(self, feature_vector, ngram):
        """Adds ngram to feature vector"""
        if ngram in self.ngrams:
            ngram_pos = self.ngrams[ngram]
            feature_vector[ngram_pos] = 1


class NgramExtractorCount(NgramExtractorBase):
    """Values a_i of feature_vector [a_1, ..., a_n] equal
        number of occurrences ngram_i in text document
    """

    def __init__(self, ns):
        super(NgramExtractorCount, self).__init__(ns)
        self.name = 'NgramExtractorCount'

    def add_ngram(self, feature_vector, ngram):
        if ngram in self.ngrams:
            ngram_pos = self.ngrams[ngram]
            feature_vector[ngram_pos] += 1