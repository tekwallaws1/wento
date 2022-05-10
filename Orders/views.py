from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from datetime import date, datetime, timedelta 
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from .filters import *
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.db.models import Q
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models import Sum, Avg, Count
from Projects.fyear import get_financial_year, get_fy_date
from Projects.basedata import projectname
 
# Create your views here.  
@login_required
def Orders_List(request, proj):
	table = Orders.objects.filter(Related_Project=proj, ds=1)
	table_fy = Orders.objects.filter(Related_Project=proj, Order_Received_Date__lte=date.today(), Order_Received_Date__gte=get_fy_date(), ds=1)
	filter_data = OrdersFilter(request.GET, queryset=table)
	table = filter_data.qs
	return render(request, 'orders/OrdersList.html', {'table_fy':table_fy, 'filter_data':filter_data})