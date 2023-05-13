from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Note(models.Model):
    title = models.CharField(max_length=26)
    text = models.CharField(max_length=1024)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)