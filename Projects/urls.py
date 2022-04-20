from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

# Projects URLs
urlpatterns = [
    path('', views.Select_Project, name='home'),
    path('modules/<proj>/', views.Select_Module, name='module'),
 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


 