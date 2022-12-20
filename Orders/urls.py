
from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static  


urlpatterns = [

    path('<firm>/<proj>/salesdb/<dur>/', views.Sales_Dashboard, name='salesdb'),

    path('<firm>/<proj>/orderslist/<status>/', views.Orders_List, name='orderslist'),
    path('<firm>/<proj>/ordersform/<fnc>/<rid>/', views.Orders_Form, name='ordersform'),

    path('<firm>/<proj>/paymentslist/<status>/<custflt>/', views.Payments_List, name='paymentslist'),
    path('<firm>/<proj>/paymentsform/<fnc>/<rid>/', views.Payments_Form, name='paymentsform'),
    path('<firm>/<proj>/orderspaymentsform/<rid>/', views.Orders_Payments_Form, name='orderspaymentsform'),

    path('<firm>/<proj>/workform/<fnc>/<rid>/', views.Work_Form, name='workform'),
    path('<firm>/<proj>/ordersworkform/<rid>/', views.Orders_Work_Form, name='ordersworkform'),
    path('<firm>/<proj>/worklist/<status>/', views.Work_Update_List, name='worklist'),

    path('<firm>/<proj>/invoice/<fnc>/<invid>/<rid>/<itemid>/<msg>/', views.Gen_Invoice, name='invoice'),
    path('<firm>/<proj>/inv_edit/<fnc>/<invid>/', views.Edit_Invoice_Form, name='editinvoice'),
    path('<firm>/<proj>/<fnc>/invoiceitem/<invid>/<itemid>/', views.Add_Item_Form, name='additem'),
    path('<firm>/<proj>/invoiceslist/<status>/', views.Invoices_List, name='invlist'),

    path('<firm>/<proj>/<fnc>/inv_deliverynote/<invid>/<rid>/', views.Invoice_Delivery_Note_Form, name='inv_deliverynote'),
    path('<firm>/<proj>/<fnc>/inv_tc/<invid>/<rid>/', views.Invoice_TC_Form, name='inv_tc'),

    path('<firm>/<proj>/inv_adjusttable/<invid>/<rowid>/<fnc>/', views.Inv_AdjustTable, name='inv_adjusttable'),

    path('<firm>/<proj>/customerwisestatement/<var1>/', views.Customer_Wise_Statement, name='customerwisestatement'),

    path('<firm>/<proj>/salesquickform/<fnc>/<qid>/', views.Sales_Quick_Form, name='salesquickform'),

    path('<firm>/<proj>/manualquoteform/<fnc>/<qid>/', views.Manual_Quote_Form, name='manualquoteform'),
    path('<firm>/<proj>/manualquoteslist/<status>/', views.Manual_Quotes_List, name='manualquoteslist'),

    path('<firm>/<proj>/paymentreceipt/<pid>/<cell>/<status>/', views.Payment_Receipt, name='paymentreceipt'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
