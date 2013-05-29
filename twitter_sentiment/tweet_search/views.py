from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

from random import choice
import json

from twitter_api_wrapper.twitter import Twitter
from classifiers.utils import load_classifier


def get_classifier():
    return load_classifier(settings.CLASSIFIER_PATH)


def home(request):
    return render(request, 'tweet_search/home.html')


def search(request):
    q = request.GET.get('q', '')

    if q:
        twitter = Twitter()
        response = twitter.search(q)
        tweets = []
        tweets_set = set([])
        classifier = get_classifier()
        for status in response[u'statuses']:
            text = status[u'text']
            if text not in tweets_set:
                tweets.append({'text': text, 'label': classifier.classify_one(text)})
                tweets_set.add(text)

        result = {'tweets': tweets}
        return HttpResponse(json.dumps(result), 'application/json')