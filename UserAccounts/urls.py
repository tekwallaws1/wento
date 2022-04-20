from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

# Projects URLs
urlpatterns = [
    # path('/<cid>/', views.Select_Project, name='select'),
 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


 