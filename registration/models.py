# from typing_extensions import Required
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Benificial(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(default="", max_length=20)
    registration_timing=models.DateTimeField(null=True)
    contact_1=models.CharField(default="", max_length=12)
    contact_2=models.CharField(default="", max_length=12)
    is_registered=models.BooleanField(default=False)
    is_delivered=models.BooleanField(default=False)
    slot_timing = models.DateTimeField(null=True)
    second_dose = models.BooleanField(default=False)	
    def __str__(self):
        return self.user.first_name

class Relatives(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(default="", max_length=20)
    registration_timing=models.DateTimeField(null=True)
    relation = models.CharField(default="", max_length=20)
    contact_1 = models.CharField(default="", max_length=12)
    contact_2 = models.CharField(default="", max_length=12)
    is_registered = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    slot_timing = models.DateTimeField(null=True)
    second_dose = models.BooleanField(default=False)
    def __str__(self):
        return self.user.first_name