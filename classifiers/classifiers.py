class ClassifierBase(object):
    def __init__(self, preprocessor, feature_extractor):
        self.preprocessor = preprocessor
        self.feature_extractor = feature_extractor

    def labels(self):
        pass

    def train(self, train_set):
        pass

    def classify(self, text):
        pass

    def batch_classify(self, test_set):
        pass