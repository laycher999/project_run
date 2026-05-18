from django.core.validators import MinValueValidator, MaxValueValidator
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

class AthleteInfo(models.Model):
    goals = models.TextField(max_length=255, blank=True, null=True)
    weight = models.IntegerField(blank=True,null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Challenge(models.Model):
    full_name = models.TextField(max_length=255)
    is_finished = models.BooleanField
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
