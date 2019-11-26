from django import forms
from .models import *
from django.forms import ModelForm

class UploadFilesForm(forms.ModelForm):
    
    class Meta:
        model=DocumentumFiles
        fields=['file_upload',]

class PostContantForm(forms.ModelForm):

    class Meta:
        model=Post
        fields=['company_code','user','content','file_url','file_name','is_private',]