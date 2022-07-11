from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

# Projects URLs
urlpatterns = [
    path('signup/', views.Signup_Form, name='signup'),
    path('<proj>/userslist/', views.Manage_User, name='users'),
    path('<proj>/employeslist/', views.Employes_List, name='employes'),
    path('<proj>/employesform/<fnc>/<eid>/', views.Employes_Form, name='employesform'),
    path('<proj>/employesbankform/<fnc>/<bid>/<eid>/', views.Employes_Bank_Form, name='employesbankform'),
    path('<proj>/employesprsnlform/<fnc>/<pid>/<eid>/', views.Employes_Prsnl_Form, name='employesprsnlform'),
    path('<proj>/editusers/<fnc>/<var>/', views.Edit_Permissions, name='edituser'),
 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


  