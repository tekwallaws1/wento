
from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('<proj>/purchasesdb/<dur>/', views.Purchases_Dashboard, name='purchasesdb'),

    path('<proj>/productslist/<status>/', views.Products_List, name='productslist'),
    path('<proj>/productsform/<status>/<fnc>/<prid>/', views.Products_Form, name='productsform'),
    path('<proj>/inventory/<status>/', views.Inventory_List, name='inventory'),
    path('<proj>/stockmovementform/<fnc>/<pid>/', views.Stock_Movement_Form, name='stockmovementform'),

    path('<proj>/purchaseslist/<status>/', views.PO_List, name='polist'),
    path('<proj>/purchasesform/<fnc>/<poid>/', views.PO_Form, name='poform'),
    
	path('<proj>/po/<fnc>/<poid>/<itemid>/<msg>/', views.Gen_PO, name='po'),
    path('<proj>/po_edit/<fnc>/<poid>/', views.Edit_PO_Form, name='editpodetails'),
    path('<proj>/<fnc>/poitem/<poid>/<itemid>/', views.Add_PO_Item_Form, name='addpoitem'),
	path('<proj>/<fnc>/po_tc/<poid>/', views.PO_TC_Form, name='po_tc'),
	path('<proj>/vendor_inv_edit/<fnc>/<invid>/', views.Edit_Vendor_Invoice_Form, name='editvendorinvoice'),

    path('<proj>/vendorpaymentslist/<status>/', views.Vendor_Payments_List, name='vendorpaymentslist'),
    path('<proj>/vendorpaymentsform/<fnc>/<payid>/', views.Vendor_Payments_Form, name='vendorpaymentsform'),
    path('<proj>/popaymentsform/<poid>/', views.PO_Payments_Form, name='popaymentsform'),

    path('<proj>/vendorinvoiceslist/<status>/', views.Vendor_Invoices_List, name='vendorinvlist'),
    path('<proj>/vendorinvoicesform/<fnc>/<poid>/<invid>/', views.Vendor_Invoice_Form, name='vendorinvoiceform'),

    path('<proj>/podeliveryform/<fnc>/<poid>/<did>/', views.PO_Delivery_Form, name='podeliveryform'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 