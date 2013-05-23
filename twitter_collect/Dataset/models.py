from django.db import models
from django.contrib.auth.models import User


class Dataset(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, null=True)

    def __unicode__(self):
        return self.name