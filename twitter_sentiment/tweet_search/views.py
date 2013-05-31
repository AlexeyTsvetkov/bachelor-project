from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

import json
from collections import Counter
import re

from twitter_api_wrapper.twitter import Twitter
from classifiers.utils import load_classifier


def remove_url(text):
    url_pattern = ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))'
    return re.sub(url_pattern, '', text)

def get_classifier(classifier_path):
    return load_classifier(classifier_path)


def stop_words():
    stop_words = set()
    with open(settings.ROOT_DIR + '/twitter_sentiment/tweet_search/stopwords.txt') as f:
        for line in f:
            stop_words.add(line.strip())
    return stop_words


def get_counter(text_set, query, sw):
    return Counter((word
                    for text in text_set
                    for word in text.lower().split()
                    if word not in sw and query not in word and
                    re.match(ur'^[$a-zA-Z0-9_]+$', word)))


def most_frequent_words(positive_text_set, negative_text_set, query):
    sw = stop_words()
    query = query.lower()
    pos = get_counter(positive_text_set, query, sw)
    neg = get_counter(negative_text_set, query, sw)
    pos.subtract(neg)
    return pos.most_common(20) + pos.most_common()[:-20:-1]


def home(request):
    return render(request, 'tweet_search/home.html')


def search(request):
    query = request.GET.get('q', '')

    if query:
        twitter = Twitter()
        tweets = []
        tweets_set = set([])
        positive = set([])
        negative = set([])
        classifier = get_classifier(settings.CLASSIFIER_PATH)

        max_id = None
        for i in xrange(1):
            if max_id:
                response = twitter.search(query, max_id=max_id)
            else:
                response = twitter.search(query)

            for status in response[u'statuses']:
                text = status[u'text']
                text_wo_url = remove_url(text)
                if not max_id or int(status[u'id']) < max_id:
                    max_id = int(status[u'id'])
                if text_wo_url not in tweets_set:
                    label = classifier.classify_one(text)

                    if label == u'positive':
                        positive.add(text_wo_url)
                    elif label == u'negative':
                        negative.add(text_wo_url)

                    tweets.append({'text': text_wo_url, 'label': label})
                    tweets_set.add(text_wo_url)

        freq = most_frequent_words(positive, negative, query)
        result = { 'tweets': tweets, 'most_frequent': freq }
        return HttpResponse(json.dumps(result), 'application/json')