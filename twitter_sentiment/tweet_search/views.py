from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

import json
from collections import Counter
import re

from twitter_api_wrapper.twitter import Twitter
from classifiers.utils import load_classifier


def get_classifier():
    return load_classifier(settings.CLASSIFIER_PATH)


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
                    re.match(ur'[a-zA-Z]+[a-zA-Z0-9\-_]*', word)))


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
        classifier = get_classifier()

        max_id = None
        for i in xrange(1):
            if max_id:
                response = twitter.search(query, max_id=max_id)
            else:
                response = twitter.search(query)

            for status in response[u'statuses']:
                text = status[u'text']
                if not max_id or int(status[u'id']) < max_id:
                    max_id = int(status[u'id'])
                if text not in tweets_set:
                    label = classifier.classify_one(text)
                    if label == u'positive':
                        positive.add(text)
                    elif label == u'negative':
                        negative.add(text)

                    tweets.append({'text': text, 'label': label})
                    tweets_set.add(text)

        freq = most_frequent_words(positive, negative, query)
        result = { 'tweets': tweets, 'most_frequent': freq }
        return HttpResponse(json.dumps(result), 'application/json')