from django.db import models

# Create your models here.

class Event(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    event_name = models.CharField(max_length=20)
    person = models.CharField(max_length=20)
    room_name = models.CharField(max_length=12)