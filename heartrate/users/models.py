from django.db import models
from django.contrib.auth.models import User


class Result(models.Model):
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    ecg = models.JSONField()
    diagnostic = models.CharField(max_length=520)


class Video(models.Model):
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    video_file = models.FileField(upload_to='videos/')
