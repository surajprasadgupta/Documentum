from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from Company.models import *
from django.utils.text import slugify


# Create your models here.

class DocumentumFiles(models.Model):
    file_upload=models.FileField(upload_to = 'static/upload_files/', default = '')
    uploaded_on = models.DateField(auto_now_add=True)


class Tags(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=225, unique=False, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Tags, self).save(*args, **kwargs)
    def __str__(self):
        return self.slug    

class Post(models.Model):
    company_code= models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField( blank=True)        
    tags = models.ManyToManyField(Tags)
    created_on = models.DateField(auto_now_add=True)
    file_url = models.URLField(max_length=255, null=True, blank=True)
    file_name=models.CharField(max_length=255, blank=True)
    is_private=models.BooleanField(default=False, blank=True)
    

    # def  __str__(self):
    #     return self.company_code
