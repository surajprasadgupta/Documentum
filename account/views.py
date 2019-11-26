from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse


# Create your views here.
def user_register(request):
    print("succddddddddddddddddddddddddddddess")

    return render(request,"file_upload.html")

def account_login(request):
    print("succegffffhss")

    redirect('/')    
