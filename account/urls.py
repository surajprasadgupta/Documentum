from django.urls import path
from documentum_app.views import *
from account.views import *
from django.conf import settings

app_name="account"

urlpatterns=[
    path('register',user_register, name="user_register"),
    path('log-in',account_login,name='account_login'),
    
]