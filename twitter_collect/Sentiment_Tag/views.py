from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse

from twitter_collect.Sentiment_Tag.forms import SearchForm, DatasetForm
from twitter_api_wrapper.twitter import Twitter

import json


def home(request):
    return render(request, 'Sentiment_Tag/home.html')

@login_required
def search_tweets(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            twitter = Twitter()
            query = form.cleaned_data.get('query')
            language = form.cleaned_data.get('language')
            max_id = form.cleaned_data.get('max_id')
            since_id = form.cleaned_data.get('since_id')
            count = int(form.cleaned_data.get('count'))

            if since_id:
                tweets = twitter.search(query, language, count, since_id=since_id)
            elif max_id:
                tweets = twitter.search(query, language, count, max_id=max_id)
            else:
                tweets = twitter.search(query, language, count)

            tweets_list = [t[u'text'] for t in tweets[u'statuses']]

            return HttpResponse(json.dumps(tweets_list), mimetype='text/javascript')
        else:
            return HttpResponseBadRequest()

    if request.method == 'GET':
        search_form = SearchForm(initial={'page': 1})
        dataset_form = DatasetForm()

        return render(request, 'Sentiment_Tag/search.html', {'search_form': search_form,
                                                             'dataset_form': dataset_form})
