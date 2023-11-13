from django.db import models

# Create your models here.

class Reccdb(models.Model):
    hotelname = models.CharField(max_length=100, primary_key=True)
    uk = models.IntegerField()
    spain = models.IntegerField()
    france = models.IntegerField()
    netherland = models.IntegerField()
    austria = models.IntegerField()
    italy = models.IntegerField()
    business = models.IntegerField()
    leisure = models.IntegerField()
    solo = models.IntegerField()
    couple = models.IntegerField()
    group = models.IntegerField()

class User(models.Model):
    name = models.CharField(max_length=50)