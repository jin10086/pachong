from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import ArrayField,JSONField
# Create your models here.

class zhihudaiguang(models.Model):
    imageurl = ArrayField(models.TextField())
    id = models.CharField(max_length=50,primary_key=True)
    is_vote_up = models.BooleanField(default=False)
    is_sex = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    href = models.CharField(max_length=100)
    content = models.TextField()
    data_score = models.FloatField()