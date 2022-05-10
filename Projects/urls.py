from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

# Projects URLs
urlpatterns = [
    path('', views.Select_Project, name='home'),
    path('modules/<proj>/', views.Select_Module, name='module'),

    path('<proj>/customerform/<fnc>/<rid>/', views.CustDt_Form, name='custform'),
    path('<proj>/customercontactform/<fnc>/<rid>/', views.CustContDt_Form, name='custcontform'),
    path('<proj>/customerslist/', views.CustDt_List, name='custlist'),

    path('<proj>/vendorform/<fnc>/<rid>/', views.VendDt_Form, name='vendform'),
    path('<proj>/vendorcontactform/<fnc>/<rid>/', views.VendContDt_Form, name='vendcontform'),
    path('<proj>/vendorslist/', views.VendDt_List, name='vendlist'),
 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 


 