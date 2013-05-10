class ClassifierBase(object):
    def __init__(self, preprocessor, feature_extractor):
        pass

    def train(self, train_set):
        pass

    def classify(self, text):
        pass

    def save(self, path):
        pass

    def load(self, path):
        pass