from django.shortcuts import render, redirect
from .forms import *
from Projects.forms import *
from django.contrib import messages
from datetime import date, datetime, timedelta   
from django.http import HttpResponse, JsonResponse 
from django.views.generic import View
from .filters import *
from django.shortcuts import get_object_or_404, render
from django.db import IntegrityError 
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.db.models import Q
from django.utils.datastructures import MultiValueDictKeyError 
from django.db.models import Sum, Avg, Count
from Projects.fyear import get_financial_year, get_fy_date, get_fy_date_fy
from Projects.basedata import projectname, firmname, customer_updateledger, permissions
from .customfunctions import inv_due_agnst_pay, balance_inv_dues1, workstatus, updateduedays, get_invoice_number, inv_amoumt_update, inv_amount_exceed, adjust_payments_to_invoices, genOrderNo, postform, paymentdelete
from num2words import num2words
from django.urls import reverse 

# import pywhatkit
# from heyoo import WhatsApp

# # t1 = datetime.now()
# # print(t1.hour, t1.minute)
# # pywhatkit.sendwhatmsg('+919848581797', 'Message 1<br>Juu', datetime.now().hour, (datetime.now().minute)+1)


# # messenger = WhatsApp('EAAQ05ybCOLgBAE1eRQWN9T3zJRNITGSEbKZC5CQqBLbn0DLOaNHoq3NMwpy9JftgfY8I7tDMdxohBKGczeB5Bn6wILcNNkwQLVSpMKx7iRVjkrsnMVvp1x0mF83CQZCl5SZCE7L3aAanZCyAT7ADhLFsfObL09cUFR8ZBW48swhZBicJrxhKBuZB5x0FwESqgoFAYXMImZAU9AZDZD',phone_number_id='104251299209410')
# # # For sending a Text messages
# # messenger.send_message('Hello I am WhatsApp Cloud API', '919848581797')
# # # For sending an Image
# # # messenger.send_image(
# # #         image="https://i.imgur.com/YSJayCb.jpeg",
# # #         recipient_id="91989155xxxx",
# # #     )
# # return HttpResponse('k')

# from twilio.rest import Client

# # client credentials are read from TWILIO_ACCOUNT_SID and AUTH_TOKEN
# sid = "AC5135be712a160e7b156cb82a197799d6"
# token = "22b6d1991f5aac2a96075ff3adf3468a"

# client = Client(sid, token)

# # this is the Twilio sandbox testing number
# from_whatsapp_number='whatsapp:+14155238886'
# # replace this number with your own WhatsApp Messaging number
# to_whatsapp_number='whatsapp:+919985691222'

# client.messages.create(body='Ahoy, world!',
#                        from_=from_whatsapp_number,
#                        to=to_whatsapp_number)

# return HttpResponse('k')

na_message = '<h3>You do not have authorisation to access this page. Get permissions to get this page. <br>Go back or select another page</h3>'
 
# Create your views here.   
@login_required
def Sales_Dashboard(request, firm, proj, dur):
	if permissions(request, 'Received Orders Dashboard', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)	
	pjl = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	pjl1 = {'Order_No__Related_Project__isnull':False} if proj == 'All' else {'Order_No__Related_Project':pdata['pj']}
	pjl2 = {'Order__Related_Project__isnull':False} if proj == 'All' else {'Order__Related_Project':pdata['pj']}
	usr = Account.objects.get(user=request.user)
	if usr.Only_Their_Works == 1:
		pjl = {'Related_Project__isnull':False, 'user':usr} if proj == 'All' else {'Related_Project':pdata['pj'], 'user':usr}
		pjl2 = {'Order__Related_Project__isnull':False, 'Order__user':usr} if proj == 'All' else {'Order__Related_Project':pdata['pj'], 'Order__user':usr}
		pjl1 = {'Order_No__Related_Project__isnull':False, 'Order_No__user':usr} if proj == 'All' else {'Order_No__Related_Project':pdata['pj'], 'Order_No__user':usr}

	if dur == 'FY':
		orders = Orders.objects.filter(RC__Short_Name=firm, **pjl, Order_Type='Confirmed', Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=get_fy_date_fy(), ds=1).order_by('Order_Received_Date')
		payments = Payment_Status.objects.filter(**pjl1,  Payment_Date__date__lte=date.today(), Payment_Date__date__gte=get_fy_date_fy()).order_by('Payment_Date')
	elif dur == 'All':
		orders = Orders.objects.filter(RC__Short_Name=firm, **pjl, Order_Type='Confirmed', ds=1).order_by('Order_Received_Date')
		payments = Payment_Status.objects.filter(**pjl1).order_by('Payment_Date')		
	else:
		orders = Orders.objects.filter(RC__Short_Name=firm, **pjl, Order_Type='Confirmed', Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=date.today()-timedelta(days=int(dur)), ds=1).order_by('Order_Received_Date')
		payments = Payment_Status.objects.filter(**pjl1,  Payment_Date__date__lte=date.today(), Payment_Date__date__gte=date.today()-timedelta(days=int(dur))).order_by('Payment_Date')

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
	invs = Invoices.objects.filter(Order__RC__Short_Name=firm, **pjl2, Lock_Status=1)
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
		
	return render(request, 'orders/SalesDashboard.html', {'pdata':pdata, 'firm':firm, 'customers_list':customers_list, 't_orders':t_orders,
		't_billed':t_billed, 't_rec_pay':t_rec_pay, 't_due_pay':t_due_pay, 't_unbilled':t_unbilled, 'order_date':order_date, 'order_val':order_val, 
		'cust_list':cust_list, 'dur':dur, 'pay_val':pay_val, 'pay_date':pay_date, 'pay_cust':pay_cust, 'count':count, 'val':val})

@login_required
def Orders_List(request, firm, proj, status):	
	if permissions(request, 'Received Orders', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	pjl = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	usr = Account.objects.get(user=request.user)
	if usr.Only_Their_Works == 1:
		pjl = {'Related_Project__isnull':False, 'user':usr} if proj == 'All' else {'Related_Project':pdata['pj'], 'user':usr}

	if status == 'Inprogress':
		table = Orders.objects.filter(RC__Short_Name=firm, **pjl, Final_Status=0, ds=1).order_by('-Order_Received_Date', 'Final_Status')
		table_fy = Orders.objects.filter(RC__Short_Name=firm, **pjl, Final_Status=0, Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=get_fy_date(), ds=1).order_by('-Order_Received_Date', 'Final_Status')
	else:
		table = Orders.objects.filter(RC__Short_Name=firm, **pjl, ds=1).order_by('-Order_Received_Date', 'Final_Status')
		table_fy = Orders.objects.filter(RC__Short_Name=firm, **pjl, Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=get_fy_date(), ds=1).order_by('-Order_Received_Date', 'Final_Status')

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
	billed, received, bills_count, t_received, t_billed, t_bills_count, po_due = 0, 0, 0, [], [], [], []
	for x in table_data:
		if x.Billing_Status:
			bills = Invoices.objects.filter(Order=x, Is_Proforma=False, Lock_Status=1)
			for y in bills:
				billed = billed + y.Invoice_Amount
				paid = paid + (y.Invoice_Amount - y.Due_Amount)
				bills_count = bills_count + 1
			t_billed.append(int(billed))
			po_due.append(int(x.Order_Value-billed))
			t_bills_count.append(bills_count)
			t_received.append(paid)
			billed=0
			paid = 0
			bills_count = 0	
		else:
			t_billed.append(int(billed))
			t_bills_count.append(bills_count)
			t_received.append(paid)
			po_due.append(x.Order_Value)

	for x in table_data:
		if x.Order_Value != None:
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

	tableset = zip(table_data, t_billed, t_received, t_bills_count, po_due)
	return render(request, 'orders/OrdersList.html', {'tableset':tableset, 'table':table_data, 'filter_data':filter_data, 'pdata':pdata, 'firm':firm, 'status':status, 
		'orders':orders, 'count':count})

@login_required
def Orders_Form(request, firm, proj, fnc, rid):
	if permissions(request, 'Received Orders', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	if proj == 'All':
		return HttpResponse('Entries/Edit/Delete Options Not Allowed, Go Back and Go to Home Page and Select Particular Project')
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(Orders, id=rid)
			form = OrdersForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				p = form.save()
				fd = Orders.objects.get(id=p.id)
				# fd.user = Account.objects.get(user=request.user)
				fd.save()
				messages.success(request, "Selected Order Details Has Been Updated")
				url = '/'+str(firm)+'/'+str(pdata['pj'])+'/orderslist/Inprogress/'
				return redirect(url)
			else:
				return render(request, 'orders/OrdersForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			getdata = get_object_or_404(Orders, id=rid)
			form = OrdersForm(instance=getdata)
			return render(request, 'orders/OrdersForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(Orders, id=rid)
		inv = Invoices.objects.filter(Order__id=rid, Lock_Status=1)
		pay = Payment_Status.objects.filter(Order_No__id=rid)
		if inv or pay:
			messages.error(request, "Due to Orders linked with this Invoices/Pyaments you can not delete this order. First check for invoices/payments, delete and then delete order still you want to delete")
		else:
			getdata.delete()
			messages.success(request, "Selected Orders Details Has Been Deleted")
		
		url = '/'+str(firm)+'/'+str(pdata['pj'])+'/orderslist/Inprogress/'
		return redirect(url)

	if request.method ==  'POST': #Create
		last_order_id = Orders.objects.filter(RC__Short_Name=firm, Order_Type='Confirmed').order_by('Order_No_1').last()
		last_order_id = last_order_id.id if last_order_id != None else None
		form = OrdersForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			fd = Orders.objects.get(id=p.id)
			fd.RC = CompanyDetails.objects.filter(Short_Name=firm).last() 
			fd.Related_Project = pdata['pj']
			# fd.user = Account.objects.get(user=request.user)
			fd.save()
			genOrderNo(request, fd.id, last_order_id)
			messages.success(request, "Order Has Been Generated")
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/orderslist/Inprogress/'
			return redirect(url)
		else:
			return render(request, 'orders/OrdersForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(Orders, id=rid)
			form = OrdersForm(instance=getdata)
			form.fields["Customer_Name"].queryset = CustDt.objects.filter(RC__Short_Name=firm, ds=1, Status=1, Address_Type='Billing')
			return render(request, 'orders/OrdersForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			form = OrdersEmptyForm()
			form.fields["Customer_Name"].queryset = CustDt.objects.filter(RC__Short_Name=firm, ds=1, Status=1, Address_Type='Billing') #load only active and non deleted customers
			form.fields["Order_Reference_Person"].queryset = CustContDt.objects.filter(Customer_Name__RC__Short_Name=firm, ds=1) #load only non deleted customers

			return render(request, 'orders/OrdersForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

#create payment from orderlsit
@login_required
def Orders_Payments_Form(request, firm, proj, rid):
	if permissions(request, 'Received Payments', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 		
	if proj == 'All':
		return HttpResponse('Entries/Edit/Delete Options Not Allowed, Go Back and Go to Home Page and Select Particular Project')
	pdata = projectname(request, proj)
	order = Orders.objects.get(id=rid)
	last_payment_status = Payment_Status.objects.filter(Order_No=order).order_by('Payment_Date')
	if request.method ==  'POST': #Create
		form = OrdersPaymentsForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			p.Order_No = order
			p.save()
			inv_due_agnst_pay(request, 'create',  p.id)
			customer_updateledger(request, 'custpay', 'create', pdata, Payment_Status.objects.get(id=p.id))
			messages.success(request, "Payment Has Been Added")
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/paymentslist/Received/custflt/'
			return redirect(url)
		else:
			return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
	else:
		form = OrdersPaymentsForm()
		return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})


#payments create and updates
@login_required
def Payments_Form(request, firm, proj, fnc, rid):
	if permissions(request, 'Received Payments', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	pdata = projectname(request, proj)
	pjl = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	pjl1 = {'Order__Related_Project__isnull':False} if proj == 'All' else {'Order__Related_Project':pdata['pj']}
	if fnc == 'edit':
		if request.method ==  'POST':
			getdata = get_object_or_404(Payment_Status, id=rid)
			form = PaymentsForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				p = form.save(commit=False)
				p= form.save()
				order = Orders.objects.get(id=p.Order_No.id)
				inv_due_agnst_pay(request, 'edit',  p.id)
				customer_updateledger(request, 'custpay', 'edit', pdata, Payment_Status.objects.get(id=p.id))
				messages.success(request, "Selected Payment Details Has Been Updated")
				url = '/'+str(firm)+'/'+str(pdata['pj'])+'/paymentslist/Received/custflt/'
				return redirect(url)
			else:
				return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			getdata = get_object_or_404(Payment_Status, id=rid)
			form = PaymentsForm(instance=getdata)
			return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

	elif fnc == 'delete': #Delete
		customer_updateledger(request, 'custpay', 'delete', pdata, Payment_Status.objects.get(id=rid))
		getdata = get_object_or_404(Payment_Status, id=rid)
		order = getdata.Order_No
		inv = getdata.Invoice_No
		dlt_amount = getdata.Received_Amount
		getdata.delete()

		order = Orders.objects.get(id=order.id)
		ag_ord = Payment_Status.objects.filter(Order_No=order).order_by('-Payment_Date')
		ag_cust = Payment_Status.objects.filter(Order_No__Customer_Name=order.Customer_Name).order_by('-Payment_Date')

		if ag_ord == None and ag_cust == None:
			messages.success(request, "Selected Payment Details Has Been Deleted")
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/paymentslist/Received/custflt/'
			return redirect(url)
		else:
			if ag_ord:
				last_pay = ag_ord.last()
			else:
				last_pay = ag_cust.last()
			order.Payment_Status = last_pay
			order.save()
			order = Purchases.objects.get(id=order.id)
			paymentdelete(request, order.id, inv.id, dlt_amount) if inv != None else None

			messages.success(request, "Selected Payment Details Has Deleted")
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/paymentslist/Received/custflt/'
			return redirect(url)

	if request.method ==  'POST': #Create
		form = PaymentsForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save(commit=False)
			if p.Order_No==None and p.Invoice_No==None:
				messages.error(request, "Either Order Details or Invoice Details Must Be Geiven to Record Payment")
				url = '/'+str(firm)+'/'+str(pdata['pj'])+'/paymentslist/Received/custflt/'
				return redirect(url)
			p= form.save()
			if not p.Order_No: # when payment through invoice number
				p.Order_No = p.Invoice_No.Order
				p.save()
				inv_due_agnst_pay(request, 'create',  p.id)
			else:
				inv_due_agnst_pay(request, 'create',  p.id)
			customer_updateledger(request, 'custpay', 'create', pdata, Payment_Status.objects.get(id=p.id))
			messages.success(request, "Payment Has Been Added")
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/paymentslist/Received/custflt/'
			return redirect(url)
		else:
			return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(Payment_Status, id=rid)
			form = PaymentsForm(instance=getdata)
			return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			form = PaymentsEmptyForm()
			form.fields["Order_No"].queryset = Orders.objects.filter(RC__Short_Name=firm, **pjl, Order_Type='Confirmed').filter(Q(Payment_Status__isnull=True)|Q(Payment_Status__isnull=False))
			form.fields["Invoice_No"].queryset = Invoices.objects.filter(Order__RC__Short_Name=firm, **pjl1, Lock_Status=1, Is_Proforma=0, Due_Amount__gt=0)
			return render(request, 'orders/PaymentsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})


@login_required
def Payments_List(request, firm, proj, status, custflt):
  if permissions(request, 'Received Payments', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
  pdata = projectname(request, proj)
  pjl = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
  pjl1 = {'Order__Related_Project__isnull':False} if proj == 'All' else {'Order__Related_Project':pdata['pj']}
  pjl2 = {'Order_No__Related_Project__isnull':False} if proj == 'All' else {'Order_No__Related_Project':pdata['pj']}
  usr = Account.objects.get(user=request.user)
  if usr.Only_Their_Works == 1:
  	pjl = {'Related_Project__isnull':False, 'user':usr} if proj == 'All' else {'Related_Project':pdata['pj'], 'user':usr}
  	pjl1 = {'Order__Related_Project__isnull':False, 'Order__user':usr} if proj == 'All' else {'Order__Related_Project':pdata['pj'], 'Order__user':usr}
  	pjl2 = {'Order_No__Related_Project__isnull':False, 'Order_No__user':usr} if proj == 'All' else {'Order_No__Related_Project':pdata['pj'], 'Order_No__user':usr}
  # for x in Invoices.objects.filter(Lock_Status=1, Order__RC__Short_Name=firm):
  # 	x.Due_Amount = x.Invoice_Amount
  # 	x.save()
  # for x in Payment_Status.objects.filter(Order_No__RC__Short_Name=firm).order_by('id'):
  # 	inv_due_agnst_pay(request, 'create', x.id)
  # 	# balance_inv_dues1(request, x.Order_No.Related_Project, x.Order_No.Customer_Name, x, x.id)
  # customers = []
  # for x in Orders.objects.filter(RC__Short_Name=firm):
  # 	customers.append(x.Customer_Name)
  # customers = list(dict.fromkeys(customers))
  # for x in customers:
  # 	balance_inv_dues1(request, x)
  # return HttpResponse('Payments Update')  

  form = PaymentsEmptyForm()
  form.fields["Order_No"].queryset = Orders.objects.filter(RC__Short_Name=firm, **pjl, Order_Type='Confirmed').filter(Q(Payment_Status__isnull=True)|Q(Payment_Status__isnull=False))
  form.fields["Invoice_No"].queryset = Invoices.objects.filter(Order__RC__Short_Name=firm, **pjl1, Lock_Status=1, Is_Proforma=0, Due_Amount__gt=0)

  if custflt != 'custflt':
  	if usr.Only_Their_Works == 1:
  		form.fields["Invoice_No"].queryset = Invoices.objects.filter(user=usr, Order__RC__Short_Name=firm, Order__Customer_Name__Customer_Name=custflt, Due_Amount__gt=0)
  	else:
  		form.fields["Invoice_No"].queryset = Invoices.objects.filter(Order__RC__Short_Name=firm, Order__Customer_Name__Customer_Name=custflt, Due_Amount__gt=0)

  table_data = Payment_Status.objects.filter(Order_No__RC__Short_Name=firm, **pjl2).order_by('-Payment_Date')
  # table_fy_pays = Vendor_Payment_Status.objects.filter(**pjl1, Payment_Date__date__lte=date.today(), Payment_Date__date__gte=get_fy_date()).order_by('Payment_Date')

  filter_data = PaymentsFilter1(request.GET, queryset=table_data)
  table_data = filter_data.qs
  has_filter_pays = any(field in request.GET for field in set(filter_data.get_fields()))
 
  total_billed, total_received, total_due, advance, customers = 0,0,0,0,[]
  
  if has_filter_pays: #update filter data queyset
  	for x in table_data: customers.append(x.Order_No.Customer_Name)
  	customers = list(dict.fromkeys(customers))
  else:
    for x in Orders.objects.filter(RC__Short_Name=firm, **pjl, Order_Type='Confirmed'): customers.append(x.Customer_Name)
    customers = list(dict.fromkeys(customers))
  
  for x in customers:
  	inv_list = Invoices.objects.filter(Order__RC__Short_Name=firm, **pjl1, Order__Customer_Name=x, Lock_Status=1)
  	pay_list = Payment_Status.objects.filter(Order_No__RC__Short_Name=firm, **pjl2, Order_No__Customer_Name=x)
  	if inv_list:
  		total_billed = total_billed + sum(inv_list.values_list('Invoice_Amount', flat=True))
  		total_due = total_due + sum(inv_list.values_list('Due_Amount', flat=True))
  	if pay_list:
  		total_received = total_received + sum(pay_list.values_list('Received_Amount', flat=True))
	
  advance =  (total_billed - total_received) - total_due
  if advance < 0:
  	advance = -(advance)
  	total_received = total_received - advance
  return render(request, 'orders/PaymentsList.html', {'table':table_data, 'filter_data':filter_data, 'customers':customers,
    'pdata':pdata, 'firm':firm, 'status':status, 'total_billed':total_billed, 'total_received':total_received, 'total_due':total_due, 'advance':advance, 'form_payments':form, 'custflt':custflt})


#create work from orderlsit, only create
@login_required
def Orders_Work_Form(request, firm, proj, rid):
	if permissions(request, 'Received Orders Work Progress', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
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
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/worklist/'+status+'/'
			return redirect(url)
		else:
			return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
	else:
		form = OrdersWorkForm()
		return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata, 'firm':firm})


#work create and updates
@login_required
def Work_Form(request, firm, proj, fnc, rid):
	if permissions(request, 'Received Orders Work Progress', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	pdata = projectname(request, proj)
	pjl = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
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
				url = '/'+str(firm)+'/'+str(pdata['pj'])+'/worklist/'+status+'/'
				return redirect(url)
			else:
				return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			getdata = get_object_or_404(Work_Status, id=rid)
			form = WorkForm(instance=getdata)
			return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

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
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/worklist/'+status+'/'		
			messages.success(request, "Selected Work Details Has Been Send to Recyclebin")
			return redirect(url)
		else:
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/worklist/Pending/'		
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
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/worklist/'+status+'/'
			return redirect(url)
		else:
			return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(Work_Status, id=rid)
			form = WorkForm(instance=getdata)
			return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			form = WorkEmptyForm()
			form.fields["Order_No"].queryset = Orders.objects.filter(RC__Short_Name=firm, **pjl, PO_Status=0)
			return render(request, 'orders/WorkForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

@login_required
def Work_Update_List(request, firm, proj, status):
	if permissions(request, 'Received Orders Work Progress', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	pdata = projectname(request, proj)
	pjl = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	
	table = Orders.objects.filter(RC__Short_Name=firm, **pjl, Order_Type='Confirmed', ds=1).order_by('-Order_Received_Date')
	table_fy = Orders.objects.filter(RC__Short_Name=firm, **pjl, Order_Type='Confirmed', Order_Received_Date__date__lte=date.today(), Order_Received_Date__date__gte=get_fy_date(), ds=1).order_by('-Order_Received_Date')

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

	return render(request, 'orders/WorkUpdateList.html', {'table':table_data,'filter_data':filter_data, 'pdata':pdata, 'firm':firm, 'status':status, 
		'count':count, 'inprogress':inprogress, 'delivered':delivered, 'notstarted':notstarted})

@login_required
def Gen_Invoice(request, firm, proj, fnc, invid, rid, itemid, msg):
	if permissions(request, 'View Invoice Copy', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	pdata = projectname(request, proj)
	last_invid = Invoices.objects.filter(Order__RC__Short_Name=firm, Lock_Status=1, Is_Proforma=0, Is_Manual=0).order_by('Invoice_No_1').last()
	last_invid = last_invid.id if last_invid else None
	
	if fnc == 'create' or fnc == 'create_manually':
		if permissions(request, 'Generate/Edit Online Customer Invoice', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	
	if request.method == 'POST' and fnc=='create':
		form = InvoicesForm1(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			rid = p.Order.id
			invid = p.id

	if fnc == 'create_manually':
		k = postform(request, rid, 1, fnc)

		if k == 'invlist':
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/invoiceslist/Issued/'
			return redirect(url)
		elif k == 'orderslist':
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/orderslist/Inprogress/'
			return redirect(url)
		else:
			form = ManualInvoicesForm()
			return render(request, 'orders/ManualInvoiceForm.html', {'form':form, 'pdata':pdata})
		
	order = Orders.objects.get(id=rid)
	
	if inv_amount_exceed(request, rid)==1 and fnc == 'create':
		url = '/'+str(firm)+'/'+str(pdata['pj'])+'/orderslist/Inprogress/'
		return redirect(url)
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
					inv = Invoices.objects.create(user=Account.objects.get(user=request.user), Order=order, Billing_From=CompanyDetails.objects.filter(Short_Name=firm).last(), 
					Billing_To=order.Customer_Name, Shipping_To=order.Customer_Name, Bank_Details=Bank_Accounts.objects.filter(RC__Short_Name=firm).last(), 
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
				dtc = Sales_TC.objects.filter(RC__Short_Name=firm).last()
				if dtc:
					tc = Terms_Conditions.objects.create(Invoice_No=inv, Terms_and_Condition1=dtc.Terms_and_Condition1 or None, Terms_and_Condition2=dtc.Terms_and_Condition2 or None, 
						Terms_and_Condition3=dtc.Terms_and_Condition3 or None, Terms_and_Condition4=dtc.Terms_and_Condition4 or None)
				else:
					tc = None
			else:
				inv =Invoices.objects.get(id=invid)
		else:
			messages.error(request, 'Invoice generation not allowed due to all Invoices value under this order exceeding the order value')
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/orderslist/Inprogress/'
			return redirect(url)

	if Terms_Conditions.objects.filter(Invoice_No=inv).last():
		tc = Terms_Conditions.objects.get(Invoice_No=inv)
	else:
		tc = None
	
	tbs = Inv_Adjust_Table.objects.filter(Invoice_No=inv)
	table_list = []
	if tbs:
		ln = 0
		pre_id = 0
		for t in tbs:
			amount, total_gst, total_amount, lenth = [],[],[],[] 
			items = Copy_Billed_Items.objects.filter(Invoice_No = inv, id__gte=pre_id, id__lt=t.Row_No).order_by('id')
			for x in items:
				lenth.append(ln)
				amount.append(x.Quantity*x.Unit_Price)
				total_gst.append(x.Quantity*x.Unit_Price*x.GST/100)
				total_amount.append((x.Quantity*x.Unit_Price)+(x.Quantity*x.Unit_Price*x.GST/100))
			ln = ln + len(items)
			itm = zip(items, amount, total_gst, total_amount, lenth)
			table_list.append(itm)
			pre_id = t.Row_No

		amount, total_gst, total_amount, lenth = [],[],[],[]
		items = Copy_Billed_Items.objects.filter(Invoice_No = inv, id__gte=pre_id).order_by('id')
		for x in items:
			lenth.append(ln)
			amount.append(x.Quantity*x.Unit_Price)
			total_gst.append(x.Quantity*x.Unit_Price*x.GST/100)
			total_amount.append((x.Quantity*x.Unit_Price)+(x.Quantity*x.Unit_Price*x.GST/100))
		itm = zip(items, amount, total_gst, total_amount, lenth)
		table_list.append(itm)
	else:
		items = Copy_Billed_Items.objects.filter(Invoice_No = inv).order_by('id')
		amount, total_gst, total_amount, lenth = [],[],[],[]
		for x in items:
			lenth.append(0)
			amount.append(x.Quantity*x.Unit_Price)
			total_gst.append(x.Quantity*x.Unit_Price*x.GST/100)
			total_amount.append((x.Quantity*x.Unit_Price)+(x.Quantity*x.Unit_Price*x.GST/100))
		itm = zip(items, amount, total_gst, total_amount, lenth)
		table_list.append(itm)
	tbl_count = len(table_list)

	
	items = Copy_Billed_Items.objects.filter(Invoice_No = inv).order_by('id')
	amount, total_gst, total_amount, final_gst, final_without_tax_amount, final_with_tax_amount = [],[],[],0,0,0 
	for x in items:
		amount.append(x.Quantity*x.Unit_Price)
		total_gst.append(x.Quantity*x.Unit_Price*x.GST/100)
		total_amount.append((x.Quantity*x.Unit_Price)+(x.Quantity*x.Unit_Price*x.GST/100))
	final_gst, final_without_tax_amount, final_with_tax_amount = int(sum(total_gst)), sum(amount), int(sum(total_amount))
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

	return render(request, 'docformats/Invoice1.html', {'pdata':pdata, 'firm':firm, 'inv':inv, 'ss':ss, 'tc':tc, 'form_invoice':form_invoice,
		'form_deliverynote':form_deliverynote, 'form_tc':form_tc, 'amount_in_words':amount_in_words, 'tax_words':tax_words, 
		'item_id':itemid, 'form_item':form_item, 'fnc':fnc, 'msg':msg, 'roundoff':roundoff, 'samegst':same_gst_perc, 'table_list':table_list, 'tbl_count':tbl_count})
	
@login_required
def Edit_Invoice_Form(request, firm, proj, fnc, invid):
	if permissions(request, 'Generate/Edit Online Customer Invoice', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	pdata = projectname(request, proj)
	inv_order_id = Invoices.objects.get(id=invid).Order.id
	msg='msg'
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/invoice/edit/'+invid+'/'+str(inv_order_id)+'/itemid/'

	if fnc == 'edit_manually':
		k = postform(request, inv_order_id, invid, fnc)
		if k != 'getform':
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/invoiceslist/Issued/'
			return redirect(url)
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
				k = adjust_payments_to_invoices(request, order.id, p.id)
			else:
				# last order billing status opdate
				inv = Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0).last()
				order.Billing_Status = inv

			inv = Invoices.objects.filter(Order=p.Order, Lock_Status=1, Is_Proforma=0)
			order.Is_Billed = 1 if inv != None else 0
			order.save()
			
			if p.Lock_Status == 1:
				# p.save()
				msg = "Invoice Has Been Locked and Generated Successfully"
			else:
				msg = "Requested Details Has Been Updated Successfully"

			if p.Lock_Status == 1 and p.Is_Proforma == 0:
				ldgr = Customer_Ledger.objects.filter(Ref_No=p.Invoice_No)
				if ldgr:
					customer_updateledger(request, 'custinv', 'edit', pdata, Invoices.objects.get(id=p.id))
				else:
					customer_updateledger(request, 'custinv', 'create', pdata, Invoices.objects.get(id=p.id))
			
			if p.Lock_Status == 0:
				ldgr = Customer_Ledger.objects.filter(Ref_No=p.Invoice_No)
				if ldgr:
					customer_updateledger(request, 'custinv', 'delete', pdata, Invoices.objects.get(id=p.id))

			url = url+msg+'/'	
			return redirect(url)
		else:
			url = url+msg+'/'
			return redirect(url)
	else:
		url = url+msg+'/'
		if fnc == 'delete':
			Invoices.objects.get(id=invid).delete()
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/orderslist/Inprogress/'
			return redirect(url)
		else:
			return redirect(url)

@login_required
def Add_Item_Form(request, firm, proj, fnc, invid, itemid):
	if permissions(request, 'Generate/Edit Online Customer Invoice', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	pdata = projectname(request, proj)
	inv_order_id = Invoices.objects.get(id=invid).Order.id
	msg = 'msg'
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/invoice/edit/'+invid+'/'+str(inv_order_id)+'/itemid/'
	if request.method == 'POST':
		if fnc == 'edit':
			form = CopyBilledItemsForm(request.POST, request.FILES, instance=get_object_or_404(Copy_Billed_Items, id=itemid))
			if form.is_valid():
				p= form.save()
				if p.Quantity == None or p.Unit_Price == None or p.GST == None:
					p.Quantity = p.Quantity if p.Quantity != None else 0
					p.Unit_Price = p.Unit_Price if p.Unit_Price != None else 0
					p.GST = p.GST if p.GST != None else 0
					p.save()
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
			item = Billed_Items.objects.filter(Add_Item__Product_Name__Product_Name=copy_item.Item_From_Product.Add_Item.Product_Name.Product_Name) if copy_item.Item_From_Product != None else None
			copy_item.delete()
			item.delete() if item != None else None
			inv_amoumt_update(request, invid)
			tbs = Inv_Adjust_Table.objects.filter(Invoice_No__id=invid)
			if tbs:
				tbs.delete()
			return redirect(url)
		else:
			return redirect(url)

@login_required
def Invoice_Delivery_Note_Form(request, firm, proj, fnc, invid, rid):
	if permissions(request, 'Generate/Edit Online Customer Invoice', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	pdata = projectname(request, proj)
	inv_order_id = Invoices.objects.get(id=invid).Order.id
	msg = 'msg'
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/invoice/edit/'+invid+'/'+str(inv_order_id)+'/itemid/'
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
def Invoice_TC_Form(request, firm, proj, fnc, invid, rid):
	if permissions(request, 'Generate/Edit Online Customer Invoice', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	pdata = projectname(request, proj)
	inv_order_id = Invoices.objects.get(id=invid).Order.id
	msg = 'msg'
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/invoice/edit/'+invid+'/'+str(inv_order_id)+'/itemid/'
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
def Invoices_List(request, firm, proj, status):
	if permissions(request, 'Customer Invoices List', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	pdata = projectname(request, proj)
	# print('ggg', Invoices.objects.values('Invoice_No').annotate(Count('id')).order_by().filter(id__count__gt=1))
	
	pjl = {'Order__Related_Project__isnull':False} if proj == 'All' else {'Order__Related_Project':pdata['pj']}
	pjl1 = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	
	usr = Account.objects.get(user=request.user)
	if usr.Only_Their_Works == 1:
		pjl = {'Order__Related_Project__isnull':False, 'Order__user':usr} if proj == 'All' else {'Order__Related_Project':pdata['pj'], 'Order__user':usr}
		pjl1 = {'Related_Project__isnull':False, 'user':usr} if proj == 'All' else {'Related_Project':pdata['pj'], 'user':usr}
	
	form = InvoicesForm1()
	form.fields["Order"].queryset = Orders.objects.filter(RC__Short_Name=firm, **pjl1, Can_Gen_Invoice=1)
	
	# update invoices due dates
	invoiceslist = Invoices.objects.filter(Order__RC__Short_Name=firm, **pjl, Last_Update__lt=date.today(), Due_Amount__gt=0, Lock_Status=1, Is_Proforma=0)
	if invoiceslist:
		for x in invoiceslist:
			x.Last_Update = date.today()
			x.save()
			updateduedays(request, x.id) 

	table_data = Invoices.objects.filter(Order__RC__Short_Name=firm, **pjl).order_by('-Invoice_Date')
	# table_fy_inv = Invoices.objects.filter(**pjl, Invoice_Date__date__lte=date.today(), Invoice_Date__date__gte=get_fy_date()).order_by('-Invoice_Date')
	
	filter_data = InvoicesFilter(request.GET, queryset=table_data)
	table_data = filter_data.qs
	
	# has_filter_inv = any(field in request.GET for field in set(filter_data.get_fields()))
	# if has_filter_inv: #update filter data queyset
	# 	filter_data = InvoicesFilter(request.GET, queryset=table_inv)
	# 	table_inv = filter_data.qs
	# 	table_data = table_inv

	full_due_inv, part_due_inv, full_clear_inv, total_billing, total_rec, adv, advance = 0, 0, 0, 0, 0, 0, 0
	fdc, pdc, fcc, tbc = 0, 0, 0, 0 #count
	orders_list, invoices_list  = [], []

	if status == 'Issued':
		table_data = table_data.filter(Lock_Status=1, Is_Proforma=0)
	elif status == 'Proforma':
		table_data = table_data.filter(Lock_Status=1, Is_Proforma=1)
	else:
		table_data = table_data.filter(Lock_Status=0, Is_Proforma=0)
	
	if table_data:
		for a in table_data:
			if a.Due_Amount != None:
				if a.Due_Amount == a.Invoice_Amount:
					full_due_inv = full_due_inv + a.Invoice_Amount
					fdc = fdc + 1
				elif  1 > a.Due_Amount >= 0:
					full_clear_inv = full_clear_inv + a.Invoice_Amount
					fcc = fcc + 1
				elif a.Due_Amount > 0 and a.Due_Amount != a.Invoice_Amount:
					part_due_inv = part_due_inv + a.Due_Amount
					pdc = pdc + 1
				else:
					pass
		total_billing = sum(table_data.values_list('Invoice_Amount', flat=True)) or 0
		tbc = len(table_data)

		for x in table_data:
			orders_list.append(x.Order)
		orders_list = list(dict.fromkeys(orders_list))

		for x in orders_list:
			pay = Payment_Status.objects.filter(Order_No=x).order_by('Payment_Date')
			if pay:
				total_rec = total_rec + sum(pay.values_list('Received_Amount', flat=True))
			inv = table_data.filter(Order=x)
			invoices_list.append(inv)

			# if still not billed against advance payments
			adv0 = Payment_Status.objects.filter(Order_No=x, Invoice_No__isnull=True).order_by('Payment_Date')
			if adv0:
				inv0 = Invoices.objects.filter(Order=adv0.last().Order_No)
				if inv0 :
					pass
				else:
					adv = sum(adv0.values_list('Received_Amount', flat=True)) + adv
	
	advance = (total_billing - (full_due_inv + part_due_inv)) - total_rec
	if advance < 0:
		advance = -(advance)
		advance = advance + adv
		total_rec = total_rec - advance
	else:
		advance = adv
		total_rec = total_rec - advance

	# print('adv', adv)
	# print('total rec', sum(Payment_Status.objects.all().values_list('Received_Amount', flat=True)))
	# print('advance', sum(Payment_Status.objects.filter(Invoice_No__isnull=True).values_list('Received_Amount', flat=True)))
	# print('total billing', sum(Invoices.objects.filter(Lock_Status=1).values_list('Invoice_Amount', flat=True)))
	# print('total due', sum(Invoices.objects.filter(Lock_Status=1).values_list('Due_Amount', flat=True)))
	# print('total rec agn billed', sum(Invoices.objects.filter(Lock_Status=1).values_list('Invoice_Amount', flat=True))-sum(Invoices.objects.filter(Lock_Status=1).values_list('Due_Amount', flat=True)))
	
	# for x in Orders.objects.filter(Payment_Status__isnull=False):
	# 	invoice_amount = int(sum(Invoices.objects.filter(Order=x, Lock_Status=1).values_list('Invoice_Amount', flat=True)))
	# 	invoice_due_amount = int(sum(Invoices.objects.filter(Order=x, Lock_Status=1).values_list('Due_Amount', flat=True)))
	# 	actual_received_amount = int(sum(Payment_Status.objects.filter(Order_No=x).values_list('Received_Amount', flat=True)))
	# 	actual_due_amount = int(invoice_amount - actual_received_amount)
	# 	if actual_due_amount != invoice_due_amount:
	# 		if actual_due_amount > 0:
	# 			print(x.PO_No, invoice_amount, actual_received_amount, invoice_due_amount, actual_due_amount)
	
	count = {'fdc':fdc, 'pdc':pdc, 'fcc':fcc, 'tbc':tbc}
	heads = {'full_due_inv':full_due_inv, 'part_due_inv':part_due_inv, 'full_clear_inv':full_clear_inv, 'total_billing':total_billing}
	table_items  = zip(orders_list, invoices_list)

	if permissions(request, 'Generate/Edit Online Customer Invoice', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: form = None

	return render(request, 'orders/InvoicesList.html', {'table':table_data, 'table_items':table_items, 'count':count, 'heads':heads, 
		'filter_data':filter_data, 'pdata':pdata, 'firm':firm, 'status':status, 'form':form, 'total_rec':total_rec, 'advance':advance})


def Inv_AdjustTable(request, firm, proj, invid, rowid, fnc):
	if permissions(request, 'Generate/Edit Online Customer Invoice', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	pdata = projectname(request, proj)
	inv = Invoices.objects.get(id=invid)
	url = '/'+str(firm)+'/'+str(pdata['pj'])+'/invoice/edit/'+str(inv.id)+'/'+str(inv.Order.id)+'/itemid/'
	if fnc == 'adjust':
		if rowid == None:
			msg = 'Please choose row to braek table and move to next page.'
			return redirect(url+msg+'/')
		else:
			ids = Inv_Adjust_Table.objects.filter(Invoice_No = inv)
			if ids:
				for x in ids:
					if rowid == x.Row_No:
						msg = 'Table already breaked from this row of selected item'
						return redirect(url+msg+'/')

			table_no = len(Inv_Adjust_Table.objects.filter(Invoice_No = inv)) if Inv_Adjust_Table.objects.filter(Invoice_No = inv) != None else 0
			create = Inv_Adjust_Table.objects.create(Invoice_No=inv, Table_No=table_no+1, Row_No=rowid)
			# here row id is item id
	if fnc == 'reset':
		Inv_Adjust_Table.objects.filter(Invoice_No=inv).delete()
	
	return redirect(url+'msg/')


def Customer_Wise_Statement(request, firm, proj, var1):
	if permissions(request, 'Customer Wise Statement', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	pdata = projectname(request, proj)
	pjl = {'Order__Related_Project__isnull':False} if proj == 'All' else {'Order__Related_Project':pdata['pj']}
	pjl1 = {'Order_No__Related_Project__isnull':False} if proj == 'All' else {'Order_No__Related_Project':pdata['pj']}

	usr = Account.objects.get(user=request.user)
	if usr.Only_Their_Works == 1:
		pjl = {'Order__Related_Project__isnull':False, 'Order__user':usr} if proj == 'All' else {'Order__Related_Project':pdata['pj'], 'Order__user':usr}
		pjl1 = {'Order_No__Related_Project__isnull':False, 'Order_No__user':usr} if proj == 'All' else {'Order_No__Related_Project':pdata['pj'], 'Order_No__user':usr}

	customer, billed, received, due, advance = [],[],[],[],[]
	tb, tr, td, ta = 0, 0, 0, 0
	cust = CustDt.objects.filter(ds=1)
	for x in cust:
		inv = Invoices.objects.filter(Order__RC__Short_Name=firm, **pjl, Order__Customer_Name=x, Lock_Status=1)
		pay = Payment_Status.objects.filter(Order_No__RC__Short_Name=firm, **pjl1, Order_No__Customer_Name=x)
		if inv or pay:
			if inv:
				customer.append(x)
				billed.append(sum(inv.values_list('Invoice_Amount', flat=True)))
				due.append(sum(inv.values_list('Due_Amount', flat=True)))
				tb, td = tb+sum(inv.values_list('Invoice_Amount', flat=True)), td+sum(inv.values_list('Due_Amount', flat=True))
			else:
				billed.append(None)
				due.append(None)
			if pay:
				received.append(sum(pay.values_list('Received_Amount', flat=True)))
				tr = tr + sum(pay.values_list('Received_Amount', flat=True))
			else:
				received.append(None)
			if sum(inv.values_list('Invoice_Amount', flat=True)) <= (sum(pay.values_list('Received_Amount', flat=True))):
				advance.append(sum(pay.values_list('Received_Amount', flat=True))-sum(inv.values_list('Invoice_Amount', flat=True)))
				ta = ta + sum(pay.values_list('Received_Amount', flat=True))-sum(inv.values_list('Invoice_Amount', flat=True))
			else:
				advance.append(0)
		else:
			return render(request, 'orders/CustomerWiseStatement.html', {'pdata':pdata, 'firm':firm})


	due, billed, received, advance, customer = zip(*sorted(zip(due, billed, received, advance, customer), reverse=True))
	# sort all lists equentially with reference to due

	data = zip(customer, billed, received, due, advance)
	heads = {'tb':tb, 'tr':tr, 'td':td, 'ta':ta}

	return render(request, 'orders/CustomerWiseStatement.html', {'pdata':pdata, 'firm':firm, 'data':data, 'heads':heads})


@login_required
def Sales_Quick_Form(request, firm, proj, fnc, qid):
	if permissions(request, 'Received Orders', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	if proj == 'All':
		return HttpResponse('Entries/Edit/Delete Options Not Allowed, Go Back and Go to Home Page and Select Particular Project')
	pdata = projectname(request, proj)

	if fnc == 'create' and request.method != 'POST':
		form1, form2, form3, form4 = CustomerFormQ(), OrdersFormQ(), InvoicesFormQ(), PaymentsFormQ()
		return render(request, 'orders/SalesForm.html', {'form1': form1, 'form2': form2, 'form3': form3, 'form4': form4, 'pdata':pdata, 'firm':firm})

	if request.method == 'POST':
		form1 = CustomerFormQ(request.POST, request.FILES)
		form2 = OrdersFormQ(request.POST, request.FILES)
		form3 = InvoicesFormQ(request.POST, request.FILES)
		form4 = PaymentsFormQ(request.POST, request.FILES)
		if form1.is_valid() * form2.is_valid() * form3.is_valid() * form4.is_valid():
			if fnc == 'create' : #update
				
				#customer registration form
				
				p1 = form1.save()
				p1.State_Code = p1.GST_No[0:2] if p1.GST_No != None else 0
				p1.RC = CompanyDetails.objects.filter(Short_Name=firm).last()
				p1.Short_Name = str(p1.Customer_Name.split()[0])
				p1.Customer_Type, p1.Address_Type = 'One Time Customer', 'Billing'
				p1.save()
				c1 = CustContDt.objects.filter(Customer_Name=p1).last()
				if not c1:
					CustContDt.objects.create(Customer_Name=p1, Contact_Person=p1.Customer_Name, Phone_Number_1=p1.Phone_Number_1)

				#orders form
				last_order_id = Orders.objects.filter(RC__Short_Name=firm, Order_Type='Confirmed').order_by('Order_No_1').last()
				last_order_id = last_order_id.id if last_order_id != None else None
				p2 = form2.save()
				fd = Orders.objects.get(id=p2.id)
				fd.RC = CompanyDetails.objects.filter(Short_Name=firm).last() 
				fd.Customer_Name = p1
				fd.Related_Project = pdata['pj']
				fd.user = Account.objects.get(user=request.user)
				fd.Order_Type, fd.Order_No = 'Confirmed', p2.id
				fd.save()
				# genOrderNo(request, fd.id, last_order_id)

				#invoice form
				p3 = form3.save()				
				order = Orders.objects.get(id=p2.id)
				order.Billing_Status, order.Is_Billed = p3, 1
				order.save()
				p3.Billing_To, p3.Order, p3.Lock_Status, p3.Is_Manual, p3.user, p3.Billing_From = order.Customer_Name, order, 1, 1, Account.objects.get(user=request.user), order.RC
				p3.save()
				updateduedays(request, p3.id)
				adjust_payments_to_invoices(request, order.id, p3.id)
				customer_updateledger(request, 'custinv', 'create', pdata, Invoices.objects.get(id=p3.id))


				#payments form
				p4 = form4.save()
				p4.Order_No = order
				p4.save()
				inv_due_agnst_pay(request, 'create',  p4.id)
				customer_updateledger(request, 'custpay', 'create', pdata, Payment_Status.objects.get(id=p4.id))

				return redirect('/'+str(firm)+'/'+str(pdata['pj'])+'/orderslist/Inprogress/')


@login_required
def Manual_Quote_Form(request, firm, proj, fnc, qid):
	if permissions(request, 'Generate/Edit Online Customer Quotation', 'Edit', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 	
	if proj == 'All':
		return HttpResponse('Entries/Edit/Delete Options Not Allowed, Go Back and Go to Home Page and Select Particular Project')
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(Manual_Quotes, id=qid)
			form = ManualQuotesForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				p = form.save()
				fd = Manual_Quotes.objects.get(id=p.id)
				fd.user = Account.objects.get(user=request.user)
				fd.save()
				messages.success(request, "Selected Quote Details Has Been Updated")
				return redirect('/'+str(firm)+'/'+str(pdata['pj'])+'/manualquoteslist/active/')
			else:
				return render(request, 'quotations/ManualQuotationsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			getdata = get_object_or_404(Manual_Quotes, id=rid)
			form = ManualQuotesForm(instance=getdata)
			return render(request, 'quotations/ManualQuotationsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(Manual_Quotes, id=qid)
		getdata.delete()
		messages.success(request, "Selected Quote Has Been Deleted")
		return redirect('/'+str(firm)+'/'+str(pdata['pj'])+'/manualquoteslist/active/')

	if request.method ==  'POST': #Create
		form = ManualQuotesForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			fd = Manual_Quotes.objects.get(id=p.id)
			fd.RC = CompanyDetails.objects.filter(Short_Name=firm).last() 
			fd.Related_Project = pdata['pj']
			fd.user = Account.objects.get(user=request.user)
			fd.save()
			messages.success(request, "Quote Has Been Generated")
			return redirect('/'+str(firm)+'/'+str(pdata['pj'])+'/manualquoteslist/active/')
		else:
			return render(request, 'quotations/ManualQuotationsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(Manual_Quotes, id=qid)
			form = ManualQuotesForm(instance=getdata)
			form.fields["Customer_Name"].queryset = CustDt.objects.filter(RC__Short_Name=firm, ds=1, Status=1, Address_Type='Billing')
			return render(request, 'quotations/ManualQuotationsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			form = ManualQuotesForm()
			return render(request, 'quotations/ManualQuotationsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

@login_required
def Manual_Quotes_List(request, firm, proj, status):
	if permissions(request, 'Customer Quotations', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message)
	pdata = projectname(request, proj)
	pjl = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	usr = Account.objects.get(user=request.user)
	if usr.Only_Their_Works == 1:
		pjl = {'Related_Project__isnull':False, 'user':usr} if proj == 'All' else {'Related_Project':pdata['pj'], 'user':usr}
	table = Manual_Quotes.objects.filter(RC__Short_Name=firm, **pjl).order_by('-Date')
	return render(request, 'quotations/ManualQuotationsList.html', {'firm':firm, 'pdata':pdata, 'table':table, 'status':status})

def Payment_Receipt(request, firm, proj, pid, cell, status):
	# if permissions(request, 'Received Payments', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message)
	pdata = projectname(request, proj)
	pjl = {'Order__Related_Project__isnull':False} if proj == 'All' else {'Order__Related_Project':pdata['pj']}

	pay = Payment_Status.objects.get(id=pid)

	if (pay.Order_No.Order_Reference_Person and pay.Order_No.Order_Reference_Person.Phone_Number_1 == cell) or pay.Order_No.Customer_Name.Phone_Number_1:	
		if pay.Invoice_No:
			inv = Invoices.objects.filter(Invoice_No=pay.Invoice_No.Invoice_No).last()
			pays = Payment_Status.objects.filter(Invoice_No=inv).order_by('Payment_Date')
			tpay = sum(pays.values_list('Received_Amount', flat=True))
			tdue = inv.Invoice_Amount - tpay
		else:
			pays = Payment_Status.objects.filter(id=pid).order_by('Payment_Date')
			tpay = sum(pays.values_list('Received_Amount', flat=True))
			tdue = pay.Order_No.Order_Value - tpay
			inv = None
	else:
		pays, inv = None, None

	return render(request, 'orders/PaymentReceipt.html', {'firm':firm, 'pdata':pdata, 'pays':pays, 'inv':inv, 'cpay':pay, 'tpay':tpay, 'tdue':tdue})
