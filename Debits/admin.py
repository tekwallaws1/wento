from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

@admin.register(Expenses)
@admin.register(Exp_Items)
@admin.register(Debit_Amounts)
@admin.register(Staff_Advances)
@admin.register(Attendance)
@admin.register(Monthatnd)
@admin.register(Working_Days)
@admin.register(DeclareDayAs)
@admin.register(Monthly_Salaries) 


class ExpensesAdmin(ImportExportModelAdmin):
	pass