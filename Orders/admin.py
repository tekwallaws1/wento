from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

@admin.register(Orders)
@admin.register(Sales_Product)

class OrdersAdmin(ImportExportModelAdmin):
	pass

