from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

# Projects URLs
urlpatterns = [
    path('signup/', views.Signup_Form, name='signup'),
    path('<firm>/<proj>/userslist/', views.Manage_User, name='users'),
    path('<firm>/<proj>/employeslist/<status>/', views.Employes_List, name='employes'),
    path('<firm>/<proj>/employesform/<fnc>/<eid>/', views.Employes_Form, name='employesform'),
    path('<firm>/<proj>/employesbankform/<fnc>/<bid>/<eid>/', views.Employes_Bank_Form, name='employesbankform'),
    path('<firm>/<proj>/employesprsnlform/<fnc>/<pid>/<eid>/', views.Employes_Prsnl_Form, name='employesprsnlform'),
    path('<firm>/<proj>/editusers/<fnc>/<var>/', views.Edit_User, name='edituser'),

    path('<firm>/<proj>/employsalariesform/<fnc>/<eid>/', views.Employ_Salaries_Form, name='employsalariesform'),
    path('<firm>/<proj>/employsalarieslist/<mode>/', views.Employ_Salaries, name='employsalarieslist'),
    path('<firm>/<proj>/emplsalrevisionform/<fnc>/<rid>/', views.Empl_Sal_Revision_Form, name='emplsalrevisionform'),
    path('<firm>/<proj>/emplsalrevisions/', views.Empl_Sal_Revision, name='emplsalrevisions'),
    path('<firm>/<proj>/pagepermissionsform/<fnc>/<eid>/', views.Page_Permissions_Form, name='pagepermissionsform'),

    path('<firm>/<proj>/signup1/<aid>/', views.Signup_Form1, name='signup1'),

 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 


