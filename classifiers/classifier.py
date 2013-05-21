from classifiers import constants


class ClassifierBase(object):
    def __init__(self, preprocessor, feature_extractor):
        self.preprocessor = preprocessor
        self.feature_extractor = feature_extractor

    def learn(self, train_set, classes):
        """Learns from train_set
        train_set -- list of documents
        classes -- list of classes of corresponding documents
        both vectors must have equal lengths
        """
        raise NotImplementedError('ClassifierBase.learn')

    def classify(self, text):
        """Classifies text document
        returns document class
        """
        raise NotImplementedError('ClassifierBase.classify')

    def batch_classify(self, text_set):
        """Classifies each text document in text_set
        returns list of classes
        """
        raise NotImplementedError('ClassifierBase.batch_classify')