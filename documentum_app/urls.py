from django.urls import path
from documentum_app.views import *
from django.conf.urls.static import static
from django.conf import settings
# from account.views import *
app_name="documentum_app"

urlpatterns=[
    path('',index, name="home"),
    path('login',login,name='login'),
    path('choose-company',choose_company,name="choose_company"),
    path('dashboard',dashboard,name="dashboard"),
    path('dashboard',dashboard,name='dashboard'),
    path('file_upload',file_upload,name='file_upload'),
    path('register',user_register, name="user_register"),
    path('log-in',account_login,name='account_login'),
    path('logout',account_logout,name='account_logout'),
    path('search',search_keyword,name='search_keyword'),
    path('create_contant',create_contant,name='create_contant'),
    path('searchby_name/',searchby_name,name='searchby_name'),
    path('searchfor_modal',searchfor_modal,name='searchfor_modal')
    

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)