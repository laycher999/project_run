from django.db import models
from django.contrib.auth.models import User


class Run(models.Model):
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(max_length=255)

