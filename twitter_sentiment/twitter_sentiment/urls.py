from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^/?$', 'tweet_search.views.home', name='home'),
    url(r'^search_tweets/?$', 'tweet_search.views.search', name='search'),
)
