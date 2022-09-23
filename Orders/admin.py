from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

class OrdersAdmin(admin.ModelAdmin):
	search_fields = ['Customer_Name']

class InvoicesAdmin(admin.ModelAdmin):
	search_fields = ['Invoice_No']


admin.site.register(Orders, OrdersAdmin)
admin.site.register(Invoices, InvoicesAdmin)
@admin.register(Work_Status)
@admin.register(Payment_Status)
@admin.register(OrderRefNo)
@admin.register(BillRefNo)
@admin.register(Delivery_Note)
@admin.register(Billed_Items)
@admin.register(Copy_Billed_Items)
@admin.register(Sales_TC)
@admin.register(Terms_Conditions)
@admin.register(Inv_Adjust_Table)

class OrdersAdmin(ImportExportModelAdmin):
	pass

