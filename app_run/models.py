from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    class RunStatus(models.TextChoices):
        INIT = "init", "Инициализация забега"
        IN_PROGRESS = "in_progress", "Забег в процессе"
        FINISHED = "finished", "Забег окончен"

    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(max_length=255)
    status = models.TextField(choices=RunStatus, default=RunStatus.INIT)
    distance = models.FloatField(default=0)
    run_time_seconds = models.IntegerField(null=True)
    speed = models.FloatField(default=0)


class AthleteInfo(models.Model):
    goals = models.TextField(max_length=255, blank=True, null=True)
    weight = models.IntegerField(blank=True,null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Challenges(models.Model):
    full_name = models.TextField(max_length=255)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)


class Positions(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    date_time = models.DateTimeField(null=True)
    speed = models.FloatField(default=0)
    distance = models.FloatField(default=0)


class CollectibleItem(models.Model):
    user = models.ManyToManyField(User)
    name = models.TextField()
    uid = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    picture = models.URLField()
    value = models.IntegerField()


class Subscribe(models.Model):
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name='athlete')
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coach')
