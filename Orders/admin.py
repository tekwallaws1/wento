from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

class OrdersAdmin(admin.ModelAdmin):
	search_fields = ['Order_No']

class InvoicesAdmin(admin.ModelAdmin):
	search_fields = ['Invoice_No', 'Order__Customer_Name__Customer_Name']


class Payment_StatusAdmin(admin.ModelAdmin):
	search_fields = ['Order_No__Customer_Name__Customer_Name']


admin.site.register(Orders, OrdersAdmin)
admin.site.register(Invoices, InvoicesAdmin)
admin.site.register(Payment_Status, Payment_StatusAdmin)
@admin.register(Work_Status)
@admin.register(Delivery_Note)
@admin.register(Billed_Items)
@admin.register(Copy_Billed_Items)
@admin.register(Sales_TC)
@admin.register(Terms_Conditions)
@admin.register(Inv_Adjust_Table)
@admin.register(Manual_Quotes)
@admin.register(Dispatches)
@admin.register(Installations)

class OrdersAdmin(ImportExportModelAdmin):
	pass

