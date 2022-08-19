from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from datetime import date, datetime, timedelta 
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from .filters import *
from django.shortcuts import get_object_or_404, render
from django.db import IntegrityError 
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.db.models import Q
from django.utils.datastructures import MultiValueDictKeyError 
from django.db.models import Sum, Avg, Count
from Projects.fyear import get_financial_year, get_fy_date, get_fy_date_fy
from Projects.basedata import projectname
from .customfunctions import assign_paystatus_to_order, workstatus, updateduedays, get_invoice_number, inv_amoumt_update, inv_amount_exceed, adjust_payments_to_invoices, genOrderNo, postform, adj_pay_to_all_inv
from num2words import num2words
from django.urls import reverse
 
 
# Create your views here. 
@login_required
def Sales_Dashboard(request, proj, dur):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	lookup1 = {'Order_No__Related_Project__isnull':False} if proj == 'All' else {'Order_No__Related_Project':pdata['pj']}
	lookup2 = {'Order__Related_Project__isnull':False} if proj == 'All' else {'Order__Related_Project':pdata['pj']}

	if dur == 'FY':
		orders = Orders.objects.filter(**lookup, Order_Type='Confirmed', Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=get_fy_date_fy(), ds=1).order_by('Order_Received_Date')
		payments = Payment_Status.objects.filter(**lookup1,  Payment_Date__date__lte=date.today(), Payment_Date__date__gte=get_fy_date_fy()).order_by('Payment_Date')
	elif dur == 'All':
		orders = Orders.objects.filter(**lookup, Order_Type='Confirmed', ds=1).order_by('Order_Received_Date')
		payments = Payment_Status.objects.filter(**lookup1).order_by('Payment_Date')		
	else:
		orders = Orders.objects.filter(**lookup, Order_Type='Confirmed', Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=date.today()-timedelta(days=int(dur)), ds=1).order_by('Order_Received_Date')
		payments = Payment_Status.objects.filter(**lookup1,  Payment_Date__date__lte=date.today(), Payment_Date__date__gte=date.today()-timedelta(days=int(dur))).order_by('Payment_Date')

	customers_list, t_orders, t_billed, t_rec_pay, t_due_pay, t_unbilled = [], [], [], [], [], []
	order_val, order_date, cust_list, pay_val, pay_date, pay_cust = [], [], [], [], [], []
	toc, ioc, toc_30, tbc, cbc, tbc_30 = 0,0,0,0,0,0 #counts
	tov, iov, tov_30, tbv, cbv, tbv_30, tdp, trp, trp_30 = 0,0,0,0,0,0,0,0,0 #value

	# orders
	toc, tov = len(orders), (orders.aggregate(sum=Sum('Order_Value')).get('sum') or 0)
	f_30 = orders.filter(Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=date.today()-timedelta(days=30))
	toc_30, tov_30 = len(f_30), (f_30.aggregate(sum=Sum('Order_Value')).get('sum') or 0)
	ip = orders.filter(Final_Status=0)
	ioc, iov = len(ip), ip.aggregate(sum=Sum('Order_Value')).get('sum') or 0

	# billing
	invs = Invoices.objects.filter(**lookup2, Lock_Status=1)
	f_30 = invs.filter(Invoice_Date__date__lte=date.today(), Invoice_Date__date__gte=date.today()-timedelta(days=30))
	tbc, tbv = len(invs), (invs.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0)
	tbc_30, tbv_30 = len(f_30), (f_30.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0)
	cbc, cbv = len(invs.filter(Due_Amount=0)), (invs.filter(Due_Amount=0).aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0)

	# payments_30 days
	trp_30 = payments.filter(Payment_Date__date__lte=date.today(), Payment_Date__date__gte=date.today()-timedelta(days=30)).aggregate(sum=Sum('Received_Amount')).get('sum') or 0

	for x in orders:
		cust_list.append(x.Customer_Name.Short_Name)
		order_val.append(int(x.Order_Value))
		order_date.append(str((x.Order_Received_Date+timedelta(days=1)).strftime('%m-%d-%Y')))
	
	customers_list = list(dict.fromkeys(cust_list))

	for x in payments:
		pay_cust.append(x.Order_No.Customer_Name.Short_Name)
		pay_val.append(int(x.Received_Amount))
		lst = [str((x.Payment_Date+timedelta(days=1)).strftime('%m-%d-%Y')), int(x.Received_Amount), int(x.Received_Amount)]
		pay_date.append(lst)

	#total billings and payments **Customer Wise
	for x in customers_list:
		ordr = orders.filter(Customer_Name__Short_Name=x)
		t_ord = ordr.aggregate(sum=Sum('Order_Value')).get('sum')
		t_orders.append(int(t_ord))

		billed, pay, due, unbilled = 0, 0, 0, 0
		for y in ordr:
			billed = billed + (Invoices.objects.filter(Order=y, Lock_Status=1).aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0)
			pay = pay + (Payment_Status.objects.filter(Order_No=y).aggregate(sum=Sum('Received_Amount')).get('sum') or 0)
		due = billed - pay
		unbilled = t_ord - billed

		# due = 0 if due < 0 else due
		unbilled = 0 if unbilled < 0 else unbilled

		t_billed.append(int(billed))
		t_rec_pay.append(int(pay))
		t_due_pay.append(int(due))
		t_unbilled.append(int(unbilled))

	trp = sum(pay_val) #total rec pay
	tdp = tbv - trp #total due
	count = {'toc':toc, 'toc_30':toc_30, 'ioc':ioc, 'tbc':tbc, 'tbc_30':tbc_30, 'cbc':cbc}
	val = {'tov':tov, 'tov_30':tov_30, 'iov':iov, 'tbv':tbv, 'tbv_30':tbv_30, 'cbv':cbv, 'trp':trp, 'trp_30':trp_30, 'tdp':tdp}
		
	return render(request, 'orders/SalesDashboard.html', {'pdata':pdata, 'customers_list':customers_list, 't_orders':t_orders,
		't_billed':t_billed, 't_rec_pay':t_rec_pay, 't_due_pay':t_due_pay, 't_unbilled':t_unbilled, 'order_date':order_date, 'order_val':order_val, 
		'cust_list':cust_list, 'dur':dur, 'pay_val':pay_val, 'pay_date':pay_date, 'pay_cust':pay_cust, 'count':count, 'val':val})

# @login_required
# def Orders_List(request, proj, status):
# 	pdata = projectname(request, proj)
# 	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
# 	# lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
# 	if status == 'Inprogress':
# 		table = Orders.objects.filter(**lookup, Final_Status=0, ds=1).order_by('-Order_Received_Date', 'Final_Status')
# 		table_fy = Orders.objects.filter(**lookup, Final_Status=0, Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=get_fy_date(), ds=1).order_by('-Order_Received_Date', 'Final_Status')
# 	else:
# 		table = Orders.objects.filter(**lookup, ds=1).order_by('-Order_Received_Date', 'Final_Status')
# 		table_fy = Orders.objects.filter(**lookup, Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=get_fy_date(), ds=1).order_by('-Order_Received_Date', 'Final_Status')

# 	# initiall it will take financial year table_fy data **when no filter applies
# 	# if any filter apply ut should take noram table
# 	filter_data = OrdersFilter(request.GET, queryset=table_fy)
# 	table_fy = filter_data.qs
# 	table_data = table_fy
# 	has_filter = any(field in request.GET for field in set(filter_data.get_fields()))
	
# 	if has_filter: #update filter data queyset
# 		filter_data = OrdersFilter(request.GET, queryset=table)
# 		table = filter_data.qs
# 		table_data = table
	
# 	if status == 'Pipeline':
# 		table_data = table_data.filter(Order_Type='Pipeline')
# 	else:
# 		table_data = table_data.filter(Order_Type='Confirmed')

# 	total, closed, inprogress, pipeline, tc, cc, ic, pc = 0,0,0,0,0,0,0,0
# 	billed, received, bills_count, t_received, t_billed, t_bills_count = 0, 0, 0, [], [], []
# 	for x in table_data:
# 		if x.Billing_Status:
# 			bills = Invoices.objects.filter(Order=x, Is_Proforma=False, Lock_Status=1)
# 			for y in bills:
# 				billed = billed + y.Invoice_Amount
# 				bills_count = bills_count + 1
# 			t_billed.append(int(billed))
# 			t_bills_count.append(bills_count)
# 			billed=0
# 			bills_count = 0
# 		else:
# 			t_billed.append(int(billed))
# 			t_bills_count.append(bills_count)
		
# 		if x.Payment_Status:
# 			pays = Payment_Status.objects.filter(Order_No=x)
# 			for z in pays:
# 				received = received + z.Received_Amount
# 			t_received.append(int(received))
# 			received=0
# 		else:
# 			t_received.append(int(received))

# 	for x in table_data:
# 		if x.Order_Type == 'Confirmed':
# 			total, tc = int(total + x.Order_Value), tc+1
# 		if x.Order_Type == 'Pipeline':
# 			pipeline, pc = int(pipeline + x.Order_Value), pc+1
# 		elif x.Final_Status == 1:
# 			closed, cc = int(closed + x.Order_Value), cc+1
# 		else:
# 			inprogress, ic = int(inprogress + x.Order_Value), ic+1	
# 	orders = {'total':total, 'closed':closed, 'inprogress':inprogress, 'pipeline':pipeline}
# 	count = {'tc':tc, 'cc':cc, 'ic':ic, 'pc':pc}

# 	tableset = zip(table_data, t_billed, t_received, t_bills_count)
# 	return render(request, 'orders/OrdersList.html', {'tableset':tableset, 'table':table_data, 'filter_data':filter_data, 'pdata':pdata, 'status':status, 
# 		'orders':orders, 'count':count})

@login_required
def Orders_List(request, proj, status):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	# lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	if status == 'Inprogress':
		table = Orders.objects.filter(**lookup, Final_Status=0, ds=1).order_by('-Order_Received_Date', 'Final_Status')
		table_fy = Orders.objects.filter(**lookup, Final_Status=0, Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=get_fy_date(), ds=1).order_by('-Order_Received_Date', 'Final_Status')
	else:
		table = Orders.objects.filter(**lookup, ds=1).order_by('-Order_Received_Date', 'Final_Status')
		table_fy = Orders.objects.filter(**lookup, Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=get_fy_date(), ds=1).order_by('-Order_Received_Date', 'Final_Status')

	# initiall it will take financial year table_fy data **when no filter applies
	# if any filter apply ut should take noram table
	filter_data = OrdersFilter(request.GET, queryset=table_fy)
	table_fy = filter_data.qs
	table_data = table_fy
	has_filter = any(field in request.GET for field in set(filter_data.get_fields()))
	
	if has_filter: #update filter data queyset
		filter_data = OrdersFilter(request.GET, queryset=table)
		table = filter_data.qs
		table_data = table
	
	if status == 'Pipeline':
		table_data = table_data.filter(Order_Type='Pipeline')
	else:
		table_data = table_data.filter(Order_Type='Confirmed')

	total, closed, inprogress, pipeline, tc, cc, ic, pc, paid = 0,0,0,0,0,0,0,0,0
	billed, received, bills_count, t_received, t_billed, t_bills_count = 0, 0, 0, [], [], []
	for x in table_data:
		if x.Billing_Status:
			bills = Invoices.objects.filter(Order=x, Is_Proforma=False, Lock_Status=1)
			for y in bills:
				billed = billed + y.Invoice_Amount
				paid = paid + (y.Invoice_Amount - y.Due_Amount)
				bills_count = bills_count + 1
			t_billed.append(int(billed))
			t_bills_count.append(bills_count)
			t_received.append(paid)
			billed=0
			paid = 0
			bills_count = 0	
		else:
			t_billed.append(int(billed))
			t_bills_count.append(bills_count)
			t_received.append(paid)
		
		# if x.Payment_Status:
		# 	pays = Payment_Status.objects.filter(Order_No=x)
		# 	for z in pays:
		# 		received = received + z.Received_Amount
		# 	t_received.append(int(received))
		# 	received=0
		# else:
		# 	t_received.append(int(received))


	for x in table_data:
		if x.Order_Type == 'Confirmed':
			total, tc = int(total + x.Order_Value), tc+1
		if x.Order_Type == 'Pipeline':
			pipeline, pc = int(pipeline + x.Order_Value), pc+1
		elif x.Final_Status == 1:
			closed, cc = int(closed + x.Order_Value), cc+1
		else:
			inprogress, ic = int(inprogress + x.Order_Value), ic+1	
	orders = {'total':total, 'closed':closed, 'inprogress':inprogress, 'pipeline':pipeline}
	count = {'tc':tc, 'cc':cc, 'ic':ic, 'pc':pc}

	tableset = zip(table_data, t_billed, t_received, t_bills_count)
	return render(request, 'orders/OrdersList.html', {'tableset':tableset, 'table':table_data, 'filter_data':filter_data, 'pdata':pdata, 'status':status, 
		'orders':orders, 'count':count})

@login_required
def Orders_Form(request, proj, fnc, rid):
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(Orders, id=rid)
			form = OrdersForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				p = form.save()
				fd = Orders.objects.get(id=p.id)
				fd.user = Account.objects.get(user=request.user)
				fd.save()
				messages.success(request, "Selected Order Details Has Been Updated")
				return redirect('/%s/orderslist/Inprogress/'%pdata['pj'])
			else:
				return render(request, 'orders/OrdersForm.html', {'form': form, 'pdata':pdata})
		else:
			getdata = get_object_or_404(Orders, id=rid)
			form = OrdersForm(instance=getdata)
			return render(request, 'orders/OrdersForm.html', {'form': form, 'pdata':pdata})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(Orders, id=rid)
		getdata.delete()
		messages.success(request, "Selected Orders Details Has Been Send to Recyclebin")
		return redirect('/%s/orderslist/Inprogress/'%pdata['pj'])

	if request.method ==  'POST': #Create
		last_order_id = Orders.objects.filter(Order_Type='Confirmed').order_by('Order_No_1').last()
		last_order_id = last_order_id.id if last_order_id != None else None
		form = OrdersForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			fd = Orders.objects.get(id=p.id) 
			fd.Related_Project = pdata['pj']
			fd.user = Account.objects.get(user=request.user)
			fd.save()
			genOrderNo(request, fd.id, last_order_id)
			messages.success(request, "Order Has Been Generated")
			return redirect('/%s/orderslist/Inprogress/'%pdata['pj'])
		else:
			return render(request, 'orders/OrdersForm.html', {'form': form, 'pdata':pdata})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(Orders, id=rid)
			form = OrdersForm(instance=getdata)
			return render(request, 'orders/OrdersForm.html', {'form': form, 'pdata':pdata})
		else:
			form = OrdersEmptyForm()
			form.fields["Customer_Name"].queryset = CustDt.objects.filter(ds=1, Status=1) #load only active and non deleted customers
			form.fields["Order_Reference_Person"].queryset = CustContDt.objects.filter(ds=1) #load only non deleted customers

			return render(request, 'orders/OrdersForm.html', {'form': form, 'pdata':pdata})

#create payment from orderlsit, only create
@login_required
def Orders_Payments_Form(request, proj, rid):
	pdata = projectname(request, proj)
	order = Orders.objects.get(id=rid)
	last_payment_status = Payment_Status.objects.filter(Order_No=order).order_by('Payment_Date')
	if request.method ==  'POST': #Create
		form = OrdersPaymentsForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			assign_paystatus_to_order(request, p.id, order.id)
			adjust_payments_to_invoices(request, order.id)
			adj_pay_to_all_inv(request, order.Customer_Name)
			messages.success(request, "Payment Has Been Added")
			return redirect('/%s/paymentslist/Received/'%pdata['pj'])
		else:
			return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata})
	else:
		form = OrdersPaymentsForm()
		return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata})


#payments create and updates
@login_required
def Payments_Form(request, proj, fnc, rid):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	lookup1 = {'Order__Related_Project__isnull':False} if proj == 'All' else {'Order__Related_Project':pdata['pj']}
	if fnc == 'edit':
		if request.method ==  'POST':
			getdata = get_object_or_404(Payment_Status, id=rid)
			form = PaymentsForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				p = form.save(commit=False)
				p= form.save()
				order = Orders.objects.get(id=p.Order_No.id)
				assign_paystatus_to_order(request, p.id, order.id)
				adjust_payments_to_invoices(request, order.id)
				adj_pay_to_all_inv(request, p.Order_No.Customer_Name)
				messages.success(request, "Selected Payment Details Has Been Updated")
				return redirect('/%s/paymentslist/Received/'%pdata['pj'])
			else:
				return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata})
		else:
			getdata = get_object_or_404(Payment_Status, id=rid)
			form = PaymentsForm(instance=getdata)
			return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(Payment_Status, id=rid)
		order = getdata.Order_No
		getdata.delete()
		order = Orders.objects.get(id=order.id)
		adjust_payments_to_invoices(request, order.id)
		adj_pay_to_all_inv(request, order.Customer_Name)
		if not order.Payment_Status:
			order.Payment_Status = Payment_Status.objects.filter(Order_No=order).order_by('Payment_Date').last()
			order.save()
		messages.success(request, "Selected Payment Details Has Deleted")
		return redirect('/%s/paymentslist/Received/'%pdata['pj'])

	if request.method ==  'POST': #Create
		form = PaymentsForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save(commit=False)
			if p.Order_No==None and p.Invoice_No==None:
				messages.error(request, "Either Order Details or Invoice Details Must Be Geiven to Record Payment")
				return redirect('/%s/paymentslist/Received/'%pdata['pj'])
			p= form.save()
			if not p.Order_No: # when paymentbthrough invoice number
				p.Order_No = p.Invoice_No.Order
				p.save()
				assign_paystatus_to_order(request, p.id, p.Order_No.id)
			else:
				assign_paystatus_to_order(request, p.id, p.Order_No.id)
			order = Orders.objects.get(id=p.Order_No.id)
			adjust_payments_to_invoices(request, order.id)
			adj_pay_to_all_inv(request, p.Order_No.Customer_Name)
			messages.success(request, "Payment Has Been Added")
			return redirect('/%s/paymentslist/Received/'%pdata['pj'])
		else:
			return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(Payment_Status, id=rid)
			form = PaymentsForm(instance=getdata)
			return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata})
		else:
			form = PaymentsEmptyForm()
			form.fields["Order_No"].queryset = Orders.objects.filter(**lookup, Order_Type='Confirmed').filter(Q(Payment_Status__isnull=True)|Q(Payment_Status__isnull=False))
			form.fields["Invoice_No"].queryset = Invoices.objects.filter(**lookup1, Lock_Status=1, Is_Proforma=0, Due_Amount__gt=0)
			return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata})

# Create your views here. 
@login_required
def Payments_List(request, proj, status):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	lookup1 = {'Order__Related_Project__isnull':False} if proj == 'All' else {'Order__Related_Project':pdata['pj']}
	total, estimate, received, due, overdue, advance= 0,0,0,0,0,0
	
	form = PaymentsEmptyForm()
	form.fields["Order_No"].queryset = Orders.objects.filter(**lookup, Order_Type='Confirmed').filter(Q(Payment_Status__isnull=True)|Q(Payment_Status__isnull=False))
	form.fields["Invoice_No"].queryset = Invoices.objects.filter(**lookup1, Lock_Status=1, Is_Proforma=0, Due_Amount__gt=0)
	
	lookup = {'Order_No__Related_Project__isnull':False} if proj == 'All' else {'Order_No__Related_Project':pdata['pj']}
	table_pays = Payment_Status.objects.filter(**lookup).order_by('Payment_Date')
	table_fy_pays = Payment_Status.objects.filter(**lookup, Payment_Date__date__lte=date.today(), Payment_Date__date__gte=get_fy_date()).order_by('Payment_Date')
	

	filter_data = PaymentsFilter(request.GET, queryset=table_fy_pays)
	table_fy_pays = filter_data.qs
	table_data = table_fy_pays
	has_filter_pays = any(field in request.GET for field in set(filter_data.get_fields()))
	
	if has_filter_pays: #update filter data queyset
		filter_data = PaymentsFilter(request.GET, queryset=table_pays)
		table_pays = filter_data.qs
		table_data = table_pays

	pays_list, bills_list, t_rec, t_due, adv, t_billed, due_date, isallbill_clear, t_adv, advances, = [], [], [], [], [], [], [], [], 0, 0
	t_due_all, t_due_overdue, t_due_unbilled, t_due_coming, total_billed, total_balance_as_advance = 0,0,0,0,0, 0

	orders_table_data = []
	for x in table_data:
		orders_table_data.append(Orders.objects.get(id=x.Order_No.id))

	orders_table_data = list(dict.fromkeys(orders_table_data))
	# table_data = orders_table_data
	
	for x in orders_table_data:
		pays 	 = Payment_Status.objects.filter(Order_No=x).order_by('Payment_Date')
		bills    = Invoices.objects.filter(Order=x, Lock_Status=1, Is_Proforma=0).order_by('Invoice_Date')
		for p in pays:
			if p.Payment_Type=='Advance':
				t_adv = t_adv + p.Received_Amount
		if pays:
			pays_list.append(pays)
			rec = pays.aggregate(sum=Sum('Received_Amount')).get('sum') or 0
			t_rec.append(rec)
			for k in pays:
				ad = 'True' if k.Payment_Type=='Advance' else 'False'
				if ad == 'True':
					break 
			adv.append(ad)
		else:
			pays_list.append(None)
			t_rec.append(0)
			rec = 0

		if bills:
			billtotal = bills.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0
			bills_list.append(bills)
			t_due.append(bills.aggregate(sum=Sum('Due_Amount')).get('sum') or 0)
			t_billed.append(billtotal)
			
			for j in bills: #if all bills clear no need to show note text as coming due date etc..
				dt = 'False' if j.Due_Amount==0 else 'True'
				if dt == 'True':
					break
			if dt=='True': #means all bills not clear
				for j in bills:
					dt = 'True' if j.Payment_Over_Due_Days==0 else 'False'
					if dt == 'True':
						break
			
			for n in bills:
				clr = 'False' if n.Due_Amount!=0 else 'True'
				if clr == 'False':
					break

			due_date.append(dt)
			isallbill_clear.append(clr)
		else:
			bills_list.append(None)
			t_due.append(None)
			due_date.append(None)
			t_billed.append(None)
			isallbill_clear.append(None)
			billtotal = 0

		advances = advances + t_adv
		t_adv=0

		due_overdue = 0
		due_coming = 0
		for d in bills:
			if d.Payment_Over_Due_Days > 0:
				due_overdue = due_overdue+d.Due_Amount
			else:
				due_coming = due_coming+d.Due_Amount


		t_due_overdue = t_due_overdue + due_overdue
		t_due_coming = t_due_coming + due_coming
		total_billed = total_billed + billtotal

		if billtotal < rec:
			total_balance_as_advance = total_balance_as_advance + rec - billtotal

	# t_due_unbilled = t_orders_value - total_billed - total_balance_as_advance
	t_due_all = t_due_overdue + t_due_coming
	pc = {'t_due_all':t_due_all, 't_due_overdue':t_due_overdue, 't_due_coming':t_due_coming,'total_balance_as_advance':total_balance_as_advance}

	data = zip(orders_table_data, pays_list, bills_list, t_rec, t_due, adv, t_billed, due_date, isallbill_clear)
	total_rec = sum(t_rec) or 0
	billed_rec = total_rec - total_balance_as_advance
	
	return render(request, 'orders/PaymentsList.html', {'table':table_data, 'data':data, 'filter_data':filter_data, 
		'pdata':pdata, 'status':status, 'pc':pc, 'total_rec':total_rec, 'billed_rec':billed_rec, 'advances':advances, 'form_payments':form})

#create work from orderlsit, only create
@login_required
def Orders_Work_Form(request, proj, rid):
	pdata = projectname(request, proj)
	if request.method ==  'POST': #Create
		form = OrdersWorkForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			workstatus(request, p.id, rid) #call common function for calculations
			messages.success(request, "Work Status Has Been Added")
			if p.Closing_Status == 1:
				status = 'Delivered'
			else:
				status = 'Inprogress'
			url = '/'+str(pdata['pj'])+'/worklist/'+status+'/'
			return redirect(url)
			# return redirect('/%s/orderslist/Inprogress/'%pdata['pj'])
		else:
			return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata})
	else:
		form = OrdersWorkForm()
		return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata})


#work create and updates
@login_required
def Work_Form(request, proj, fnc, rid):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(Work_Status, id=rid)
			form = WorkForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				p= form.save()
				workstatus(request, p.id, p.Order_No.id)
				messages.success(request, "Selected Work Details Has Been Updated")
				if p.Closing_Status == 1:
					status = 'Delivered'
				else:
					status = 'Inprogress'
				url = '/'+str(pdata['pj'])+'/worklist/'+status+'/'
				return redirect(url)
			else:
				return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata})
		else:
			getdata = get_object_or_404(Work_Status, id=rid)
			form = WorkForm(instance=getdata)
			return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(Work_Status, id=rid)
		getdata.delete()
		lastwork = Work_Status.objects.filter(Order_No=getdata.Order_No).order_by('Date').last()
		if lastwork:
			workstatus(request, lastwork.id, lastwork.Order_No.id)
			if lastwork.Closing_Status == 1:
				status = 'Delivered'
			else:
				status = 'Inprogress'
			url = '/'+str(pdata['pj'])+'/worklist/'+status+'/'			
			messages.success(request, "Selected Work Details Has Been Send to Recyclebin")
			return redirect(url)
		else:
			url = '/'+str(pdata['pj'])+'/worklist/Pending/'		
			messages.success(request, "Selected Work Details Has Been Send to Recyclebin")
			return redirect(url)

	if request.method ==  'POST': #Create
		form = WorkForm(request.POST, request.FILES)
		if form.is_valid():
			p= form.save()
			workstatus(request, p.id, p.Order_No.id)
			messages.success(request, "Work Status Has Been Added")
			if p.Closing_Status == 1:
				status = 'Delivered'
			else:
				status = 'Inprogress'
			url = '/'+str(pdata['pj'])+'/worklist/'+status+'/'
			return redirect(url)
		else:
			return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(Work_Status, id=rid)
			form = WorkForm(instance=getdata)
			return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata})
		else:
			form = WorkEmptyForm()
			form.fields["Order_No"].queryset = Orders.objects.filter(**lookup, PO_Status=0)
			return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata})

@login_required
def Work_Update_List(request, proj, status):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	
	table = Orders.objects.filter(**lookup, Order_Type='Confirmed', ds=1).order_by('-Order_Received_Date')
	table_fy = Orders.objects.filter(**lookup, Order_Type='Confirmed', Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=get_fy_date(), ds=1).order_by('-Order_Received_Date')

	filter_data = OrdersFilter(request.GET, queryset=table_fy)
	table_fy = filter_data.qs
	table_data = table_fy
	has_filter = any(field in request.GET for field in set(filter_data.get_fields()))
	
	if has_filter: #update filter data queyset
		filter_data = OrdersFilter(request.GET, queryset=table)
		table = filter_data.qs
		table_data = table

	orders_ip, orders_dl, orders_ns, works_ip, works_dl, works_ns = [], [], [], [], [], []
	
	if status == 'Inprogress':
		table_data = table_data.filter(Work_Status__isnull=False, PO_Status=0)
	elif status == 'Delivered':
		table_data = table_data.filter(PO_Status=1)
	else: #not yet started
		table_data = table_data.filter(Work_Status=None, PO_Status=0,)

	count = len(table_data)

	for x in table_data:
		works = Work_Status.objects.filter(Order_No=x).order_by('Date') or None
		if status == 'Inprogress':
			orders_ip.append(x)
			works_ip.append(works)
		elif status == 'Delivered':
			orders_dl.append(x)
			works_dl.append(works)
		else:
			orders_ns.append(x)
			works_ns.append(works)

	inprogress = zip(orders_ip, works_ip)
	delivered = zip(orders_dl, works_dl)
	notstarted = zip(orders_ns, works_ns)

	print(orders_ip, works_ip)
	return render(request, 'orders/WorkUpdateList.html', {'table':table_data,'filter_data':filter_data, 'pdata':pdata, 'status':status, 
		'count':count, 'inprogress':inprogress, 'delivered':delivered, 'notstarted':notstarted})

@login_required
def Gen_Invoice(request, proj, fnc, invid, rid, itemid, msg):
	pdata = projectname(request, proj)
	last_invid = Invoices.objects.filter(Lock_Status=1, Is_Proforma=0, Is_Manual=0).order_by('Invoice_No_1').last()
	last_invid = last_invid.id if last_invid else None
	
	if request.method == 'POST' and fnc=='create':
		form = InvoicesForm1(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			rid = p.Order.id
			invid = p.id

	if fnc == 'create_manually':
		k = postform(request, rid, 1, fnc)
		if k == 'invlist':
			return redirect('/%s/invoiceslist/Issued/'%pdata['pj'])
		elif k == 'orderslist':
			return redirect('/%s/orderslist/Inprogress/'%pdata['pj'])
		else:
			form = ManualInvoicesForm()
			return render(request, 'orders/ManualInvoiceForm.html', {'form':form, 'pdata':pdata})
		
	order = Orders.objects.get(id=rid)
	
	if inv_amount_exceed(request, rid)==1 and fnc == 'create':
		return redirect('/%s/orderslist/Inprogress/'%pdata['pj']) 
		messages.error(request, 'Invoice generation not allowed due to all Invoices value under this order exceeding the order value')
	else:
		if order.Can_Gen_Invoice != 0:
			if fnc == 'create':
				if request.method == 'POST':
					Invoices.objects.filter(id=invid).update(user=Account.objects.get(user=request.user), Billing_From=CompanyDetails.objects.all().last(), 
					Billing_To=order.Customer_Name, Shipping_To=order.Customer_Name, Bank_Details=Bank_Accounts.objects.all().last(), 
					Invoice_Date=datetime.now(), Payment_Due_Date=date.today())
					inv = Invoices.objects.get(id=invid)
				else:
					inv = Invoices.objects.create(user=Account.objects.get(user=request.user), Order=order, Billing_From=CompanyDetails.objects.all().last(), 
					Billing_To=order.Customer_Name, Shipping_To=order.Customer_Name, Bank_Details=Bank_Accounts.objects.all().last(), 
					Invoice_Date=datetime.now(), Payment_Due_Date=date.today(), Payment_Terms = '50% Advance, Balance Against Dispatch')

				get_invoice_number(request, last_invid, inv.id)
				inv = Invoices.objects.get(id=inv.id)
				order.Billing_Status = inv
				order.save()
				order_items = Order_Items.objects.filter(Order_No=order) #check wether items addded in order
				if order_items:
					for x in order_items:
						itm = Billed_Items.objects.create(user=Account.objects.get(user=request.user), Invoice_No=inv, 
							Add_Item=FG_Price.objects.get(Product_Name=order_items.Add_Item, Quantity=order_items.Quantity))
						copy_itm = Copy_Billed_Items.objects.create(Invoice_No=inv, Item_Description=p.Add_Item.Product_Name.Product_Name, Item_Code=p.Add_Item.Product_Name.Item_Code, Quantity=itm.Quantity, UOM=order.Add_Item.Product_Name.UOM,
							Unit_Price=order.Add_Item.Unit_Price, HSN_Code=order.Add_Item.HSN_Code, GST=order.Add_Item.GST, 
							CESS=order.Add_Item.CESS, Other_Taxes=order.Add_Item.Other_Taxes, Item_From_Product=itm)
				else:
					order_items = None 
				dtc = Sales_TC.objects.all().last()
				if dtc:
					tc = Terms_Conditions.objects.create(Invoice_No=inv, Terms_and_Condition1=dtc.Terms_and_Condition1 or None, Terms_and_Condition2=dtc.Terms_and_Condition2 or None, 
						Terms_and_Condition3=dtc.Terms_and_Condition3 or None, Terms_and_Condition4=dtc.Terms_and_Condition4 or None)
				else:
					tc = None
			else:
				inv =Invoices.objects.get(id=invid)
		else:
			messages.error(request, 'Invoice generation not allowed due to all Invoices value under this order exceeding the order value')
			return redirect('/%s/orderslist/Inprogress/'%pdata['pj'])

	if Terms_Conditions.objects.filter(Invoice_No=inv).last():
		tc = Terms_Conditions.objects.get(Invoice_No=inv)
	else:
		tc = None
	
	items = Copy_Billed_Items.objects.filter(Invoice_No = inv).order_by('id')
	amount, total_gst, total_amount, final_gst, final_without_tax_amount, final_with_tax_amount = [],[],[],[],[],[] 
	for x in items:
		amount.append(x.Quantity*x.Unit_Price)
		total_gst.append(x.Quantity*x.Unit_Price*x.GST/100)
		total_amount.append((x.Quantity*x.Unit_Price)+(x.Quantity*x.Unit_Price*x.GST/100))
	final_gst, final_without_tax_amount, final_with_tax_amount = int(sum(total_gst)), sum(amount), int(sum(total_amount))

	itm = zip(items, amount, total_gst, total_amount)
	ss = {'final_gst':final_gst, 'final_without_tax_amount':final_without_tax_amount, 'final_with_tax_amount':final_with_tax_amount}

	
	form_invoice = InvoicesForm(instance=get_object_or_404(Invoices, id=inv.id))
	

	if Delivery_Note.objects.filter(Invoice_No=inv).last():
		form_deliverynote = DeliveryNoteForm(instance=get_object_or_404(Delivery_Note, Invoice_No=inv))
	else:
		lut_no = inv.Billing_From.LUT_No if inv.Billing_From.LUT_No != None else 0
		# delivery_dtls = Delivery_Note.objects.create(Invoice_No=inv, LUT_No = lut_no)
		form_deliverynote = DeliveryNoteForm(initial={'LUT_No': lut_no})
		# form_deliverynote = DeliveryNoteForm(instance=get_object_or_404(Delivery_Note, Invoice_No=inv))

	if Terms_Conditions.objects.filter(Invoice_No=inv).last():
		form_tc = InvoiceTCForm(instance=get_object_or_404(Terms_Conditions, Invoice_No=inv))
	else:
		form_tc = InvoiceTCForm()

	if itemid != 'itemid':
		form_item = CopyBilledItemsForm(instance=get_object_or_404(Copy_Billed_Items, id=itemid))
	else:
		form_item = BilledItemsForm()

	amount_in_words =  num2words(int(inv.Invoice_Amount), to='cardinal', lang='en_IN').replace(',', '').replace('-', ' ') if inv.Invoice_Amount else None 
	tax_words = num2words(int(inv.GST_Amount), to='cardinal', lang='en_IN').replace(',', '').replace('-', ' ') if inv.Invoice_Amount else None

	roundoff = inv.Invoice_Amount - int(inv.Invoice_Amount)
	
	copy_items = Copy_Billed_Items.objects.filter(Invoice_No=inv)
	same_gst_perc = []
	for x in copy_items: same_gst_perc.append(x.GST)
	same_gst_perc = list(dict.fromkeys(same_gst_perc))
	same_gst_perc = same_gst_perc[0] if len(same_gst_perc) == 1 else None
	print(same_gst_perc)

	return render(request, 'docformats/Invoice1.html', {'pdata':pdata, 'inv':inv, 'itm':itm, 'ss':ss, 'tc':tc, 'form_invoice':form_invoice,
		'form_deliverynote':form_deliverynote, 'form_tc':form_tc, 'amount_in_words':amount_in_words, 'tax_words':tax_words, 
		'item_id':itemid, 'form_item':form_item, 'fnc':fnc, 'msg':msg, 'roundoff':roundoff, 'samegst':same_gst_perc})
	
@login_required
def Edit_Invoice_Form(request, proj, fnc, invid):
	pdata = projectname(request, proj)
	inv_order_id = Invoices.objects.get(id=invid).Order.id
	msg='msg'
	url = '/'+str(pdata['pj'])+'/invoice/edit/'+invid+'/'+str(inv_order_id)+'/itemid/'

	if fnc == 'edit_manually':
		k = postform(request, inv_order_id, invid, fnc)
		if k != 'getform':
			return redirect('/%s/invoiceslist/Issued/'%pdata['pj'])
		else:
			form = ManualInvoicesForm1(instance=get_object_or_404(Invoices, id=invid))
			return render(request, 'orders/ManualInvoiceForm.html', {'form':form, 'pdata':pdata})
	
	if request.method == 'POST':
		form = InvoicesForm(request.POST, request.FILES, instance=get_object_or_404(Invoices, id=invid))
		if form.is_valid():
			p= form.save()
			updateduedays(request, p.id)
			#update when invoice locked
			if inv_amount_exceed(request, inv_order_id)==1:
				p.Lock_Status = 0
				p.save()
				msg = 'Invoice generation not allowed due to all Invoices value under related received work order exceeding the order value'
				url = url+msg+'/'
				return redirect(url)

			if p.Is_Proforma == 1: #lock status meant for main invoice
				p.Lock_Status = 1
				p.save()
						
			order = Orders.objects.get(id=p.Order.id)
			if p.Lock_Status==1 and p.Is_Proforma==0:
				order.Billing_Status = p
				k = adjust_payments_to_invoices(request, order.id)
			else:
				# last order billing status opdate
				inv = Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0).last()
				order.Billing_Status = inv

			inv = Invoices.objects.filter(Order=p.Order, Lock_Status=1, Is_Proforma=0)
			order.Is_Billed = 1 if inv != None else 0
			order.save()
			
			if p.Lock_Status == 1:
				msg = "Invoice Has Been Locked and Generated Successfully"
			else:
				msg = "Requested Details Has Been Updated Successfully"

			# if p.Set_For_Returns == 0:
			# 	msg = "Invoice Has Been Removed From GST Returns for this time Successfully"

			url = url+msg+'/'	
			return redirect(url)
		else:
			url = url+msg+'/'
			return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			Invoices.objects.get(id=invid).delete()
			return redirect('/%s/orderslist/Inprogress/'%pdata['pj'])
		else:
			return redirect(url)



@login_required
def Add_Item_Form(request, proj, fnc, invid, itemid):
	pdata = projectname(request, proj)
	inv_order_id = Invoices.objects.get(id=invid).Order.id
	msg = 'msg'
	url = '/'+str(pdata['pj'])+'/invoice/edit/'+invid+'/'+str(inv_order_id)+'/itemid/'
	if request.method == 'POST':
		if fnc == 'edit':
			form = CopyBilledItemsForm(request.POST, request.FILES, instance=get_object_or_404(Copy_Billed_Items, id=itemid))
			if form.is_valid():
				p= form.save()
				inv_amoumt_update(request, invid)
				msg = "Item Details Has Been Updated Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
		else:
			form = BilledItemsForm(request.POST, request.FILES)
			if form.is_valid():
				p = form.save()
				p = Billed_Items.objects.get(id=p.id)
				p.Invoice_No = Invoices.objects.get(id=invid)
				p.save()
				if Billed_Items.objects.filter(Invoice_No=p.Invoice_No, Add_Item=p.Add_Item).order_by('id').count() > 1:
					Billed_Items.objects.filter(Invoice_No=p.Invoice_No, Add_Item=p.Add_Item).order_by('id').last().delete()
					msg = "This Item Aleady Added, You Can Modify Quantity from Existing Items List"
					url = url+msg+'/'
					return redirect(url)
				else:
					copy_item = Copy_Billed_Items.objects.create(Invoice_No=p.Invoice_No, Item_Description=p.Add_Item.Product_Name.Product_Name, Quantity=p.Quantity, UOM=p.Add_Item.Product_Name.UOM,
				Unit_Price=p.Add_Item.Unit_Price, HSN_Code=p.Add_Item.HSN_Code, GST=p.Add_Item.GST, 
				CESS=p.Add_Item.CESS, Other_Taxes=p.Add_Item.Other_Taxes, Item_From_Product=p)
				inv_amoumt_update(request, invid)
				msg = "Item Details Has Been Updated Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			copy_item = Copy_Billed_Items.objects.get(id=itemid)
			item = Billed_Items.objects.filter(Add_Item__Product_Name__Product_Name=copy_item.Item_From_Product.Add_Item.Product_Name.Product_Name)
			copy_item.delete()
			item.delete()
			inv_amoumt_update(request, invid)
			return redirect(url)
		else:
			return redirect(url)

@login_required
def Invoice_Delivery_Note_Form(request, proj, fnc, invid, rid):
	pdata = projectname(request, proj)
	inv_order_id = Invoices.objects.get(id=invid).Order.id
	msg = 'msg'
	url = '/'+str(pdata['pj'])+'/invoice/edit/'+invid+'/'+str(inv_order_id)+'/itemid/'
	if request.method == 'POST':
		if fnc == 'edit':
			form = DeliveryNoteForm(request.POST, instance=get_object_or_404(Delivery_Note, id=rid))
			if form.is_valid():
				p= form.save()
				msg = "Delivery Note Details Has Been Updated Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
		else:
			form = DeliveryNoteForm(request.POST)
			if form.is_valid():
				p= form.save()
				p.Invoice_No = Invoices.objects.get(id=invid)
				p.save()
				inv = Invoices.objects.filter(id=invid).last()
				inv.Delivery_Note = p
				inv.save()
				msg = "Delivery Details Has Been Added Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				return HttpResponse(form.errors)
				url = url+msg+'/'
				return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			dn = Delivery_Note.objects.get(id=rid)
			dn.delete()
			return redirect(url)
		
		return redirect(url)

@login_required
def Invoice_TC_Form(request, proj, fnc, invid, rid):
	pdata = projectname(request, proj)
	inv_order_id = Invoices.objects.get(id=invid).Order.id
	msg = 'msg'
	url = '/'+str(pdata['pj'])+'/invoice/edit/'+invid+'/'+str(inv_order_id)+'/itemid/'
	if request.method == 'POST':
		if fnc == 'edit':
			form = InvoiceTCForm(request.POST, request.FILES, instance=get_object_or_404(Terms_Conditions, id=rid))
			if form.is_valid():
				p= form.save()
				msg = "Terms and Condition Details Has Been Updated Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
		else:
			form = InvoiceTCForm(request.POST, request.FILES)
			if form.is_valid():
				p= form.save()
				p.Invoice_No = Invoices.objects.get(id=invid)
				p.save()
				inv = Invoices.objects.filter(id=invid).last()
				inv.Terms_and_Conditions = p
				inv.save()
				msg = "Terms and Condition Details Has Been Added Successfully"
				url = url+msg+'/'
				return redirect(url)
			else:
				url = url+msg+'/'
				return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			tc = Terms_Conditions.objects.get(id=rid)
			tc.delete()
			return redirect(url)
		return redirect(url)

@login_required
def Invoices_List(request, proj, status):
	pdata = projectname(request, proj)
	
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	form = InvoicesForm1()
	form.fields["Order"].queryset = Orders.objects.filter(**lookup, Can_Gen_Invoice=1)
	
	lookup = {'Order__Related_Project__isnull':False} if proj == 'All' else {'Order__Related_Project':pdata['pj']}

	# update invoices due dates
	invoiceslist = Invoices.objects.filter(**lookup, Last_Update__lt=date.today(), Due_Amount__gt=0, Lock_Status=1, Is_Proforma=0)
	if invoiceslist:
		for x in invoiceslist:			
			x.Last_Update = date.today()
			x.save()
			updateduedays(request, x.id)

	table_inv = Invoices.objects.filter(**lookup).order_by('-Invoice_Date')
	table_fy_inv = Invoices.objects.filter(**lookup, Invoice_Date__date__lte=date.today(), Invoice_Date__date__gte=get_fy_date()).order_by('-Invoice_Date')
	
	filter_data = InvoicesFilter(request.GET, queryset=table_fy_inv)
	table_fy_inv = filter_data.qs
	table_data = table_fy_inv
	has_filter_inv = any(field in request.GET for field in set(filter_data.get_fields()))
	
	if has_filter_inv: #update filter data queyset
		filter_data = InvoicesFilter(request.GET, queryset=table_inv)
		table_inv = filter_data.qs
		table_data = table_inv

	full_due_inv, part_due_inv, full_clear_inv, total_billing = 0, 0, 0, 0
	fdc, pdc, fcc, tbc = 0, 0, 0, 0 #count
	orders_list, invoices_list  = [], []

	if status == 'Issued':
		table_data = table_data.filter(Lock_Status=1, Is_Proforma=0)
	elif status == 'Proforma':
		table_data = table_data.filter(Lock_Status=1, Is_Proforma=1)
	else:
		table_data = table_data.filter(Lock_Status=0, Is_Proforma=0)


	for x in table_data:
		orders_list.append(x.Order)
	orders_list = list(dict.fromkeys(orders_list))

	for x in orders_list:
		if status == 'Issued':
			inv = Invoices.objects.filter(Order=x, Lock_Status=1, Is_Proforma=0)
		elif status == 'Proforma':
			inv = Invoices.objects.filter(Order=x, Lock_Status=1, Is_Proforma=1)
		else:
			inv = Invoices.objects.filter(Order=x, Lock_Status=0, Is_Proforma=0)

		invoices_list.append(inv)
		inv = inv.filter(Invoice_Amount__isnull=False)
		inv_total 	 = sum(inv.values_list('Invoice_Amount', flat=True)) or 0
		
		total_billing = total_billing + inv_total
		tbc = tbc + len(inv)

		for a in inv:
			if a.Due_Amount:
				if a.Due_Amount == a.Invoice_Amount:
					full_due_inv = full_due_inv + a.Invoice_Amount
					fdc = fdc + 1
				elif a.Due_Amount == 0:
					full_clear_inv = full_clear_inv + a.Invoice_Amount
					fcc = fcc + 1
				elif a.Due_Amount > 0 and a.Due_Amount != a.Invoice_Amount:
					part_due_inv = part_due_inv + a.Due_Amount
					pdc = pdc + 1
				else:
					pass

	count = {'fdc':fdc, 'pdc':pdc, 'fcc':fcc, 'tbc':tbc}
	heads = {'full_due_inv':full_due_inv, 'part_due_inv':part_due_inv, 'full_clear_inv':full_clear_inv, 'total_billing':total_billing}
	table_items  = zip(orders_list, invoices_list)	
	
	return render(request, 'orders/InvoicesList.html', {'table':table_data, 'table_items':table_items, 'count':count, 'heads':heads, 
		'filter_data':filter_data, 'pdata':pdata, 'status':status, 'form':form})
