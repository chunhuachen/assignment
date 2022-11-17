from django.db import models

# Create your models here.
class Users(models.Model):
    acct = models.CharField(max_length=64, primary_key=True)
    pwd = models.CharField(max_length=128)
    fullname = models.CharField(max_length=64)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
