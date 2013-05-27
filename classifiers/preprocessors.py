import unicodedata
import sys
import re


class PreprocessorBase(object):
    def __init__(self):
        pass

    def preprocess(self, text):
        pass


class PreprocessorPunctuationRemove(PreprocessorBase):
    """

    Removes all punctuation

    """

    def __init__(self):
        super(PreprocessorPunctuationRemove, self).__init__()
        self.table = dict.fromkeys(i for i in xrange(sys.maxunicode)
                                   if unicodedata.category(unichr(i)).startswith('P'))
        self.table.pop(ord(u'_'), None)

    def preprocess(self, text):
        return text.translate(self.table)


class PreprocessorHashtagRemove(PreprocessorBase):
    """

    Removes hashtags

    """

    def __init__(self):
        super(PreprocessorHashtagRemove, self).__init__()
        self.regex = re.compile(ur'#+[\w_]+[\w\'_\-]*[\w_]+')

    def preprocess(self, text):
        return self.regex.sub(u'', text)


class PreprocessorLengtheningRemove(PreprocessorBase):
    """

    Removes lengthening

    """

    def __init__(self):
        super(PreprocessorLengtheningRemove, self).__init__()
        self.regex = re.compile(ur'(\w)\1+', re.UNICODE)

    def preprocess(self, text):
        return self.regex.sub(ur'\1\1', text)


class PreprocessorWhitespaceRemove(PreprocessorBase):
    """

    Replaces whitespace sequences with one space

    """

    def __init__(self):
        super(PreprocessorWhitespaceRemove, self).__init__()
        self.regex = re.compile(ur'\s+', re.UNICODE)

    def preprocess(self, text):
        return self.regex.sub(ur' ', text)


class PreprocessorLowercase(PreprocessorBase):
    """

    Transforms text to lowercase

    """

    def __init__(self):
        super(PreprocessorLowercase, self).__init__()

    def preprocess(self, text):
        return text.lower()


class PreprocessorUrlEncode(PreprocessorBase):
    """

    Replaces urls with URL_TOKEN
    Regexp that matches urls taken from
    http://daringfireball.net/2010/07/improved_regex_for_matching_urls

    """

    def __init__(self):
        super(PreprocessorUrlEncode, self).__init__()
        self.regex = re.compile(
            ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

    def preprocess(self, text):
        return self.regex.sub(u'URL_TOKEN', text)


class PreprocessorUserEncode(PreprocessorBase):
    """

    Replaces user mentions with MENTION_USER

    """

    def __init__(self):
        super(PreprocessorUserEncode, self).__init__()
        self.regex = re.compile(ur'@([\w_]+)')

    def preprocess(self, text):
        return self.regex.sub(ur'USERNAME', text)


class PreprocessorEmoticons(PreprocessorBase):
    """

    Replaces emoticons with corresponding sentiment token
    http://en.wikipedia.org/wiki/List_of_emoticons

    """

    def __init__(self):
        super(PreprocessorEmoticons, self).__init__()
        positive_pattern = ur'''
        ([:;=8xX]       #eyes
        [\']?           #optional tear
        [-o]*           #nose
        [3D\]\}\)]+)    #mouth
        |               #reversed
        ([\[\(\{]+
        [-o]*
        [\']?
        [:;=8])'''
        self.regex_pos = re.compile(positive_pattern, re.VERBOSE)
        negative_pattern = ur'''
        ([:=]           #eyes
        [\']?           #optional tear
        [-o]*           #nose
        [\(\[\{\\\/]+)  #mouth
        |               #reversed
        (\)\]\}\\\/]+
        [-o]*
        [\']?
        [:=])'''
        self.regex_neg = re.compile(negative_pattern, re.VERBOSE)

    def preprocess(self, text):
        text = self.regex_pos.sub(u'POSITIVE_SMILEY', text)
        return self.regex_neg.sub(u'NEGATIVE_SMILEY', text)


class CombinedPreprocessor(PreprocessorBase):
    """

    Builds chains of regular preprocessors

    """

    def __init__(self, preprocessors):
        super(CombinedPreprocessor, self).__init__()
        self.preprocessors = preprocessors

    def append(self, preprocessor):
        self.preprocessors.append(preprocessor)

    def preprocess(self, text):
        for preprocessor in self.preprocessors:
            text = preprocessor.preprocess(text)
        return text


def build_preprocessor_from_args(args):
    preprocessors = []
    if args.lowercase:
        preprocessors.append(PreprocessorLowercase())
    if args.encode_urls:
        preprocessors.append(PreprocessorUrlEncode())
    if args.encode_mentions:
        preprocessors.append(PreprocessorUserEncode())
    if args.encode_emoticons:
        preprocessors.append(PreprocessorEmoticons())
    if args.remove_hashtags:
        preprocessors.append(PreprocessorHashtagRemove())
    if args.remove_lengthening:
        preprocessors.append(PreprocessorLengtheningRemove())
    if args.remove_punctuation:
        preprocessors.append(PreprocessorPunctuationRemove())
    if args.remove_whitespace:
        preprocessors.append(PreprocessorWhitespaceRemove())

    if args.all_preprocessors:
        preprocessors = [PreprocessorLowercase(), PreprocessorUrlEncode(),
                         PreprocessorUserEncode(), PreprocessorEmoticons(),
                         PreprocessorHashtagRemove(), PreprocessorLengtheningRemove(),
                         PreprocessorPunctuationRemove(), PreprocessorWhitespaceRemove()]

    return CombinedPreprocessor(preprocessors)


def build_combined_preprocessor():
    preprocessors = [PreprocessorLowercase(), PreprocessorUrlEncode(),
                     PreprocessorUserEncode(), PreprocessorEmoticons(),
                     PreprocessorHashtagRemove(), PreprocessorLengtheningRemove(),
                     PreprocessorPunctuationRemove(), PreprocessorWhitespaceRemove()]

    return CombinedPreprocessor(preprocessors)