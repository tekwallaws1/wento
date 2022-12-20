
from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [ 
    
    path('<firm>/<proj>/purchasesdb/<dur>/', views.Purchases_Dashboard, name='purchasesdb'),

    path('<firm>/<proj>/productslist/<status>/', views.Products_List, name='productslist'),
    path('<firm>/<proj>/productsform/<status>/<fnc>/<prid>/', views.Products_Form, name='productsform'),
    path('<firm>/<proj>/inventory/<status>/', views.Inventory_List, name='inventory'),
    path('<firm>/<proj>/stockmovementform/<fnc>/<pid>/', views.Stock_Movement_Form, name='stockmovementform'),

    path('<firm>/<proj>/purchaseslist/<status>/', views.PO_List, name='polist'),
    path('<firm>/<proj>/purchasesform/<fnc>/<poid>/', views.PO_Form, name='poform'),
    
	path('<firm>/<proj>/po/<fnc>/<poid>/<itemid>/<msg>/', views.Gen_PO, name='po'),
    path('<firm>/<proj>/po_edit/<fnc>/<poid>/', views.Edit_PO_Form, name='editpodetails'),
    path('<firm>/<proj>/<fnc>/poitem/<poid>/<itemid>/', views.Add_PO_Item_Form, name='addpoitem'),
	path('<firm>/<proj>/<fnc>/po_tc/<poid>/', views.PO_TC_Form, name='po_tc'),
	path('<firm>/<proj>/vendor_inv_edit/<fnc>/<invid>/', views.Edit_Vendor_Invoice_Form, name='editvendorinvoice'),

    path('<firm>/<proj>/vendorpaymentslist/<status>/<vendflt>/', views.Vendor_Payments_List, name='vendorpaymentslist'),
    path('<firm>/<proj>/vendorpaymentsform/<fnc>/<payid>/', views.Vendor_Payments_Form, name='vendorpaymentsform'),
    path('<firm>/<proj>/popaymentsform/<poid>/', views.PO_Payments_Form, name='popaymentsform'),

    path('<firm>/<proj>/vendorinvoiceslist/<status>/', views.Vendor_Invoices_List, name='vendorinvlist'),
    path('<firm>/<proj>/vendorinvoicesform/<fnc>/<poid>/<invid>/', views.Vendor_Invoice_Form, name='vendorinvoiceform'),

    path('<firm>/<proj>/podeliveryform/<fnc>/<poid>/<did>/', views.PO_Delivery_Form, name='podeliveryform'),

    path('<firm>/<proj>/quotationslist/<status>/', views.Quotation_List, name='quotationslist'),
    path('<firm>/<proj>/quotationsform/<fnc>/<qid>/', views.Quotation_Form, name='quotesform'),
    path('<firm>/<proj>/genquote/<fnc>/<qid>/<itemid>/<msg>/', views.Gen_Quotation, name='genquote'),
    path('<firm>/<proj>/quote_edit/<fnc>/<qid>/', views.Edit_Quotation_Form, name='quote_edit'),
    path('<firm>/<proj>/<fnc>/quoteitem/<qid>/<itemid>/', views.Add_Quotation_Item_Form, name='quoteitem'),
    path('<firm>/<proj>/<fnc>/quote_tc/<qid>/', views.Quotation_TC_Form, name='quote_tc'),

    path('<firm>/<proj>/uploadquote/<qid>/', views.Upload_Quote, name='uploadquote'),
    path('<firm>/<proj>/vendorwisestatement/<var1>/', views.Vendor_Wise_Statement, name='vendorwisestatement'),

    path('<firm>/<proj>/vendorpaymentreceipt/<pid>/<cell>/<status>/', views.Vendor_Payment_Receipt, name='vendorpaymentreceipt'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 