import numpy as np
import math


class BaseFeatureSelector(object):
    def __init__(self, feature_extractor, top):
        self.feature_extractor = feature_extractor
        self.name = 'FeatureSelectorBase'
        self.top = top

    def __str__(self):
        return 'FeatureSelector=%s (top = %f), %s' % (self.name, self.top, str(self.feature_extractor))

    def features_count(self):
        return len(self.best_features)

    def get_feature_scores(self, documents, labels, feature_count):
        raise NotImplementedError()

    def learn(self, documents, labels):
        best_features = set([])
        self.feature_extractor.learn(documents, labels)
        f_num = self.feature_extractor.features_count()
        if 0.0 < self.top <= 1.0:
            top_num = f_num * self.top
        else:
            top_num = self.top

        scores = self.get_feature_scores(documents, labels, f_num)
        class_count = len(set(labels))

        for Class in xrange(class_count):
            features = zip(range(f_num), list(scores[Class]))
            features.sort(key=lambda x: x[1], reverse=True)
            best_for_class = map(lambda x: x[0], features[:int(1.0 * top_num / class_count)])
            for feature in best_for_class:
                best_features.add(feature)

        self.best_features = list(best_features)

    def extract(self, document):
        orig_features = self.feature_extractor.extract(document)
        features = np.zeros((self.features_count(),))
        for i in xrange(self.features_count()):
            features[i] = orig_features[self.best_features[i]]
        return features


class MutualInformationFeatureSelector(BaseFeatureSelector):
    def __init__(self, feature_extractor, top):
        super(MutualInformationFeatureSelector, self).__init__(feature_extractor, top)
        self.name = 'MISelector'

    def get_feature_scores(self, documents, labels, feature_count):
        classes = set(labels)
        class_count = len(classes)
        FV = map(self.feature_extractor.extract, documents)
        MI = np.zeros((len(classes), feature_count))
        FC = np.zeros((feature_count, class_count))
        FS = np.zeros((feature_count,))
        CF = np.zeros((class_count, ))
        N = 4.0

        for i in xrange(len(documents)):
            label = labels[i]
            for Feature in xrange(feature_count):
                feature_instance = FV[i][Feature]
                FC[Feature][label] += feature_instance
                CF[label] += feature_instance
                N += feature_instance

        for Feature in xrange(feature_count):
            FS[Feature] = np.sum(FC[Feature])

        for Class in xrange(class_count):
            for Feature in xrange(feature_count):
                n_11 = FC[Feature][Class] + 1.
                n_10 = FS[Feature] - FC[Feature][Class] + 1.
                n_01 = CF[Class] - FC[Feature][Class] + 1.
                n_00 = N - (n_11 + n_10 + n_01)

                n_1x = n_11 + n_10
                n_x1 = n_11 + n_01
                n_0x = n_00 + n_01
                n_x0 = n_00 + n_10
                MI[Class][Feature] = (n_11 / N) * math.log(N * n_11 / (n_1x * n_x1), 2) + \
                                     (n_10 / N) * math.log(N * n_10 / (n_1x * n_x0), 2) + \
                                     (n_01 / N) * math.log(N * n_01 / (n_0x * n_x1), 2) + \
                                     (n_00 / N) * math.log(N * n_00 / (n_0x * n_x0), 2)

        return MI


class DeltaIdfFeatureSelector(BaseFeatureSelector):
    def __init__(self, feature_extractor, top):
        super(DeltaIdfFeatureSelector, self).__init__(feature_extractor, top)
        self.name = 'DeltaIdf'

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

    def get_feature_scores(self, documents, labels, feature_count):
        classes = set(labels)
        class_count = len(classes)
        class_feature_counts = np.zeros((class_count, feature_count))
        class_document_count = [0. for i in xrange(class_count)]

        for i in xrange(len(documents)):
            document, label = documents[i], labels[i]
            feature_vector = self.feature_extractor.extract(document)
            class_feature_counts[label] += feature_vector
            class_document_count[label] += 1

        features_deltas = []
        for Class1 in xrange(class_count):
            features_delta = np.log2(class_document_count[Class1] / (class_feature_counts[Class1] + 1.))
            for Class2 in xrange(class_count):
                if Class1 != Class2:
                    features_delta -= np.log2(class_document_count[Class2] / (class_feature_counts[Class2] + 1.))
            features_deltas.append(features_delta)

        return features_deltas
