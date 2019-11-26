from django.urls import path
# from documentum_app.views import *
from Company.views import *
from django.conf.urls.static import static
from django.conf import settings

app_name="Company"
urlpatterns = [
  
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)