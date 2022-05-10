
from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.mainp, name='home'),
    
    path('orderslist/<proj>/', views.Orders_List, name='orderslist'),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
