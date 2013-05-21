import cStringIO
import csv
import pickle
import codecs
from classifiers import constants


class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def read_labelled_set(input_file_path):
    messages = []
    labels = []

    with open(input_file_path, 'rt') as f_in:
        reader = UnicodeReader(f_in)

        for row in reader:
            message = row[1]
            label = row[2]
            if label == u'positive':
                label = constants.POSITIVE_CODE
            elif label == u'negative':
                label = constants.NEGATIVE_CODE

            if label == constants.POSITIVE_CODE or label == constants.NEGATIVE_CODE:
                messages.append(message)
                labels.append(label)

    return messages, labels


def save_classifier(path, classifier):
    with open(path, 'wb') as f:
        pickle.dump(classifier, f)


def load_classifier(path):
    with open(path, 'rb') as f:
        classifier = pickle.load(f)
    return classifier