from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

# Projects URLs
urlpatterns = [
    path('', views.Select_Firm, name='home'),
    path('<firm>/selectproject/', views.Select_Project, name='selectproject'),
    path('<firm>/<proj>/modules/', views.Select_Module, name='module'),

    path('<firm>/<proj>/customerform/<fnc>/<rid>/', views.CustDt_Form, name='custform'),
    path('<firm>/<proj>/customercontactform/<fnc>/<rid>/', views.CustContDt_Form, name='custcontform'),
    path('<firm>/<proj>/customerslist/', views.CustDt_List, name='custlist'),

    path('<firm>/<proj>/vendorform/<fnc>/<rid>/', views.VendDt_Form, name='vendform'),
    path('<firm>/<proj>/vendorcontactform/<fnc>/<rid>/', views.VendContDt_Form, name='vendcontform'),
    path('<firm>/<proj>/vendorslist/', views.VendDt_List, name='vendlist'),

    path('<firm>/<proj>/companyform/<fnc>/<rid>/', views.Company_Form, name='companyform'),
    path('<firm>/<proj>/companylist/', views.Companies_List, name='companylist'),

    path('<firm>/<proj>/gst/<cat>/<months>/', views.GST_Returns, name='gst'),

    path('<firm>/<proj>/customerledger/<mode>/', views.Cust_Ledger, name='customerledger'),
    path('<firm>/<proj>/vendorledger/<mode>/', views.Vend_Ledger, name='vendorledger'),

    path('<firm>/<proj>/dailyfinancemovement/<dur>/<status>/', views.Daily_Finance, name='dailyfinancemovement'),
 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 


 