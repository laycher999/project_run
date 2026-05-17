from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    class RunStatus(models.TextChoices):
        INIT = "INIT", "Инициализация забега"
        IN_PROGRESS = "IN_PROGRESS", "Забег в процессе"
        FINISHED = "FINISHED", "Забег окончен"
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(max_length=255)
    status = models.TextField(choices=RunStatus, default=RunStatus.FINISHED)

