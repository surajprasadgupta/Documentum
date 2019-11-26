from django.db import models
from django.utils import timezone


# Create your models here.

class Company(models.Model):
    company_code=models.IntegerField(blank=True, null=True)
    company_name=models.CharField(max_length=255, blank=True)
    created_date =  models.DateField(auto_now_add=True)
    def __str__(self):
    	return self.company_name