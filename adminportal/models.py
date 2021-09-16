from django.db import models
from django.db import models
from datetime import datetime    
from django.contrib.auth.models import AbstractUser

class Addvaccines(models.Model):
    slot = models.IntegerField()
    numbers_of_vaccine = models.IntegerField()
    name_of_vaccine = models.IntegerField()
    date = models.DateField(null=True)
    extra_vaccine=models.IntegerField(default=0)