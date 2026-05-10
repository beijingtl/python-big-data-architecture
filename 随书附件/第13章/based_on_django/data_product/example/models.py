from django.db import models

class Counter(models.Model):
    pageviews = models.IntegerField("pageviews", default=0)