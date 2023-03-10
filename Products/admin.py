from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

@admin.register(Products)
@admin.register(Product_Price)
@admin.register(Purchases)
@admin.register(PO_Delivery_Status)
@admin.register(PO_Items)
@admin.register(Copy_PO_Items)
@admin.register(Purchase_TC)
@admin.register(PO_Terms_Conditions)
@admin.register(Vendor_Payment_Status)
@admin.register(Vendor_Invoices)
@admin.register(Quotes)
@admin.register(Quote_TC)
@admin.register(Quote_Items)
@admin.register(Copy_Quote_Items)
@admin.register(Quote_TC_Default)



 
class Finished_GoodsAdmin(ImportExportModelAdmin):
	pass