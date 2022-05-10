from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

# Projects URLs
urlpatterns = [
    path('signup/', views.Signup_Form, name='signup'),
    path('<proj>/userslist/', views.Manage_User, name='users'),
    path('<proj>/editusers/<fnc>/<var>/', views.Edit_Permissions, name='edituser'),
 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


 