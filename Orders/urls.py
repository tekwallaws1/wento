
from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [ 
    path('<proj>/orderslist/<status>/', views.Orders_List, name='orderslist'),
    path('<proj>/ordersform/<fnc>/<rid>/', views.Orders_Form, name='ordersform'),

    path('<proj>/paymentslist/<status>/', views.Payments_List, name='paymentslist'),
    path('<proj>/paymentsform/<fnc>/<rid>/', views.Payments_Form, name='paymentsform'),
    path('<proj>/orderspaymentsform/<rid>/', views.Orders_Payments_Form, name='orderspaymentsform'),

    path('<proj>/workform/<fnc>/<rid>/', views.Work_Form, name='workform'),
    path('<proj>/ordersworkform/<rid>/', views.Orders_Work_Form, name='ordersworkform'),
    path('<proj>/worklist/<status>/', views.Work_Update_List, name='worklist'),

    path('<proj>/invoice/<fnc>/<invid>/<rid>/<itemid>/<msg>/', views.Gen_Invoice, name='invoice'),
    path('<proj>/inv_edit/<fnc>/<invid>/', views.Edit_Invoice_Form, name='editinvoice'),
    path('<proj>/<fnc>/invoiceitem/<invid>/<itemid>/', views.Add_Item_Form, name='additem'),
    path('<proj>/invoiceslist/<status>/', views.Invoices_List, name='invlist'),

    path('<proj>/<fnc>/inv_deliverynote/<invid>/<rid>/', views.Invoice_Delivery_Note_Form, name='inv_deliverynote'),
    path('<proj>/<fnc>/inv_tc/<invid>/<rid>/', views.Invoice_TC_Form, name='inv_tc'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
