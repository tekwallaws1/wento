from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

from django.apps import apps

# myapp = apps.get_app_config('Proposals')
# for model in myapp.get_models():
#     @admin.register(model)

@admin.register(CompanyDetails)
@admin.register(PowerCat)
@admin.register(Costing)
@admin.register(Proposal)
@admin.register(Quote)

class CompanyDetailsAdmin(ImportExportModelAdmin):
	pass