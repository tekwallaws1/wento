from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

@admin.register(Orders)
@admin.register(Work_Status)
@admin.register(Payment_Status)
@admin.register(OrderRefNo)
@admin.register(BillRefNo)
@admin.register(Invoices)
@admin.register(Delivery_Note)
@admin.register(Billed_Items)
@admin.register(Copy_Billed_Items)
@admin.register(Sales_TC)
@admin.register(Terms_Conditions)

class OrdersAdmin(ImportExportModelAdmin):
	pass

