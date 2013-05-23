from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

from Sentiment_Tag.views import home, search_tweets
from Dataset.views import create_dataset, delete_dataset, \
    export_dataset, list_datasets, view_dataset, add_tweet_to_dataset
from Twitter_Login.views import begin_auth, twitter_logout, end_auth

urlpatterns = patterns(
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^login/$', begin_auth),
    url(r'^logout/$', twitter_logout),
    url(r'^login/authenticated/$', end_auth),


    url(r'^dataset/list/$', list_datasets, name='list_datasets'),
    url(r'^dataset/create/$', create_dataset, name='create_dataset'),
    url(r'^dataset/delete/(?P<id>\d+)/$', delete_dataset, name='delete_dataset'),
    url(r'^dataset/export/$', export_dataset, name='export_dataset'),
    url(r'^dataset/(?P<id>\d+)/$', export_dataset, name='view_dataset'),
    url(r'^dataset/(?P<dataset_id>\d+)/add_tweet/$', add_tweet_to_dataset, name='add_tweet_to_dataset'),

    url(r'^tweets/search/$', search_tweets, name='search_tweets'),

    url(r'^/?$', home, name='home')
)

