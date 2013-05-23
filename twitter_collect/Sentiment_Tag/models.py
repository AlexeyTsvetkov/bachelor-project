from django.db import models
from twitter_collect.Dataset.models import Dataset

SENTIMENT_CHOICES = ((True, 'Positive'), (False, 'Negative'))
LANGUAGES = (('ru', 'Russian'), ('en', 'English'))


class Tweet(models.Model):
    language = models.CharField(max_length=2, choices=LANGUAGES)
    text = models.CharField(max_length=140)
    sentiment = models.NullBooleanField(choices=SENTIMENT_CHOICES, null=True)

    dataset = models.ForeignKey(Dataset)