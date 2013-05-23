import numpy as np


class FeatureSelectorBase(object):
    """
    Acts as feature extractor wrapper
    Does not change features
    """
    def __init__(self, feature_extractor):
        self.feature_extractor = feature_extractor
        self.name = 'None'

    def __str__(self):
        return 'FeatureSelector=%s, %s' % (self.name, str(self.feature_extractor))

    def features_count(self):
        return self.feature_extractor.features_count()

    def learn(self, documents, labels):
        self.feature_extractor.learn(documents, labels)

    def extract(self, document):
        return self.feature_extractor.extract(document)


class FeatureSelectorDeltaIdf(FeatureSelectorBase):
    """
    Selects best features based on delta idf values
    """
    def __init__(self, feature_extractor, top):
        super(FeatureSelectorDeltaIdf, self).__init__(feature_extractor)
        self.top = top
        self.best_features = []
        self.name = 'DeltaIdf (top=%s)' % (str(top),)

    def features_count(self):
        return len(self.best_features)

    def top_n_features(self, n):
        self.features_delta.sort(key=lambda x: x[1])
        get_name = lambda x: (self.feature_extractor.get_feature_name(x[0]), x[1])
        absolute = lambda x: abs(x[1])
        top = map(get_name, self.features_delta[:n])
        top.sort(key=absolute)
        bottom = map(get_name, self.features_delta[-n:])
        bottom.sort(key=absolute)
        return top, bottom

    def learn(self, documents, labels):
        classes = set(labels)
        if len(classes) != 2:
            raise ValueError('Delta TfIdf works only for 2 classes')

        self.feature_extractor.learn(documents, labels)
        f_num = self.feature_extractor.features_count()
        if 0.0 < self.top < 2:
            top_num = f_num * self.top
        else:
            top_num = self.top

        class_feature_counts = np.zeros((2, f_num))
        class_document_count = [0., 0.]
        for i in xrange(len(documents)):
            document, label = documents[i], labels[i]
            feature_vector = self.feature_extractor.extract(document)
            class_feature_counts[label] += feature_vector
            class_document_count[label] += 1

        features_delta = np.log2(class_document_count[0] / (class_feature_counts[0] + 1.)) - \
                         np.log2(class_document_count[1] / (class_feature_counts[1] + 1.))

        self.features_delta = zip(range(f_num), features_delta)

        delta_abs = np.absolute(features_delta)
        features = zip(range(f_num), list(delta_abs))
        features.sort(key=lambda x: x[1], reverse=True)
        self.best_features = map(lambda x: x[0], features[:int(top_num)])

    def extract(self, document):
        orig_features = self.feature_extractor.extract(document)
        features = np.zeros((self.features_count(),))
        for i in xrange(self.features_count()):
            features[i] = orig_features[self.best_features[i]]
        return features