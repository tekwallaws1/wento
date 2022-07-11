from datetime import date, datetime, timedelta 
from django.db.models import Sum, Avg, Count
from.models import *
from .forms import *
from django.http import HttpResponse, JsonResponse
from Projects.fyear import get_financial_year, get_fy_date
from Projects.basedata import projectname
from django.contrib import messages

def genOrderNo(request, order_id, last_order_id):
	fd = Orders.objects.get(id=order_id)
	fd.FY = get_financial_year(str(date.today()))

	last_order = Orders.objects.get(id=last_order_id) if last_order_id != None else None

	if last_order != None:		
		if fd.FY == last_order.FY:
			fd.Order_No_1 = last_order.Order_No_1 + 1
		else:
			fd.Order_No_1 = 1
	else:
		fd.Order_No_1 = 1 
	
	if len(str(fd.Order_No_1)) == 1: 
		orderno1 = '00'+str(fd.Order_No_1)
	elif len(str(fd.Order_No_1)) == 2:
		orderno1 = '0'+str(fd.Order_No_1)
	else:
		orderno1 = fd.Order_No_1	
	
	fd.Order_No = 'Orders/'+str(fd.FY)+'/'+str(orderno1)
	fd.save()


def assign_paystatus_to_order(request, pay_id, order_id):
	order = Orders.objects.get(id=order_id)
	payment = Payment_Status.objects.get(id=pay_id)
	order.Payment_Status = payment
	order.save()

	if not payment.Order_No:
		payment.Order_No = order

	inv = Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0).order_by('Invoice_Date')
	payments  = Payment_Status.objects.filter(Order_No=order).order_by('Payment_Date')
	t_inv = sum(inv.values_list('Invoice_Amount', flat=True))
	t_pay = sum(payments.values_list('Received_Amount', flat=True))
	#here t_pay = total payment received except current payment, bcz pay_status not assigned to order

	if t_inv==0 and t_pay==0:
		payment.Payment_Type = 'Advance'

	elif t_inv - t_pay > 0:
		payment.Payment_Type = 'Due'
	else:
		payment.Payment_Type = 'Advance'

	payment.user = Account.objects.get(user=request.user)
	payment.save()


def adjust_payments_to_invoices(request, orderid):
	# if invoice lock and if any payments under this order before invoice gen.
	# inv_current = Invoices.objects.filter(id=invid).last()
	order = Orders.objects.get(id=orderid)
	inv = Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0).order_by('Invoice_Date')
	payments  = Payment_Status.objects.filter(Order_No=order).order_by('Payment_Date')
	t_inv = inv.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0 if inv != None else 0
	t_pay = payments.aggregate(sum=Sum('Received_Amount')).get('sum') or 0 if payments != None else 0
	

	# CASE-1: No Prev Invoices, No Payments (only cureent gen invoice)
	if len(inv) == 1 and t_pay==0:
		for x in inv:
			x.Due_Amount = x.Invoice_Amount
			x.save()
		return 1

	# CASE-2: Previous invoices available against that order but no payments gainst order
	if len(inv) > 1 and t_pay==0:
		for x in inv:
			x.Due_Amount = x.Invoice_Amount
			x.save()
		print('return 1')
		return 2

	# CASE-3: Invoices Due Amount Adjustments Against Order and Received Paymants
	if t_inv+10 <= t_pay or t_inv-10 <= t_pay:
		# if total billing value =< total received value update all bills due as 0
		Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0).update(Due_Amount=0)
		print('return 3')
		return 3
	else:
		for x in inv:
			if t_pay > x.Invoice_Amount:
				x.Due_Amount = 0
				x.save()
				t_pay = t_pay - x.Invoice_Amount
				print('return tpay', x, t_pay)
			else:
				# means whole received payment is less than one single invoice amount
				x.Due_Amount = x.Invoice_Amount - t_pay
				t_pay = 0
				x.save()
				print('return 4')
				# Breaking for and while loops
		return 4

def workstatus(request, workid, orderid):
	fd = Work_Status.objects.get(id=workid)
	fd.user = Account.objects.get(user=request.user)
	fd.Order_No = Orders.objects.get(id=orderid)
	fd.save()
			
	# update order final statuses and payment final statuses
	order = Orders.objects.get(id=orderid)
	fd = Work_Status.objects.filter(Order_No=order).order_by('Date').last()
	order.Work_Status = fd #assign that work status id data to order
	order.save()

def updateduedays(request, invid):
	inv = Invoices.objects.filter(id=invid).last()
	inv.Payment_Due_Date = inv.Invoice_Date.date() + timedelta(days=inv.Credit_Days)
	inv.Payment_Over_Due_Days = (date.today() - inv.Payment_Due_Date).days
	if inv.Payment_Over_Due_Days < 0:
		inv.Payment_Over_Due_Days = 0
	inv.save()

def get_invoice_number(request, last_invid, invid):
	last_inv = Invoices.objects.get(id=last_invid) if last_invid != None else None
	fd = Invoices.objects.get(id=invid)

	fd.FY = get_financial_year(str(date.today()))
	if last_inv != None:		
		if fd.FY == last_inv.FY:
			fd.Invoice_No_1 = last_inv.Invoice_No_1 + 1
		else:
			fd.Invoice_No_1 = 1
	else:
		fd.Invoice_No_1 = 1 
	
	if len(str(fd.Invoice_No_1)) == 1: 
		invno1 = '00'+str(fd.Invoice_No_1)
	elif len(str(fd.Invoice_No_1)) == 2:
		invno1 = '0'+str(fd.Invoice_No_1)
	else:
		invno1 = fd.Invoice_No_1
	
	fd.Invoice_No_Format = No_Formats.objects.filter(No_Format_Related_To='Invoice').last()
	fd.Invoice_No = str(fd.Invoice_No_Format.No_Format)+str(fd.FY)+'/'+str(invno1)
	fd.save()

def inv_amoumt_update(request, invid):
	items = Billed_Items.objects.filter(Invoice_No__id=invid)
	inv_amount, gst_amount, cess_amount = 0, 0, 0
	for x in items:
		inv_amount = inv_amount + (x.Quantity*x.Add_Item.Unit_Price) + (x.Quantity*x.Add_Item.Unit_Price*x.Add_Item.GST/100)
		gst_amount = (gst_amount + (x.Quantity*x.Add_Item.Unit_Price*x.Add_Item.GST/100)) if x.Add_Item.GST else 0
		cess_amount = (cess_amount + (x.Quantity*x.Add_Item.Unit_Price*x.Add_Item.CESS/100)) if x.Add_Item.CESS else 0
	inv = Invoices.objects.filter(id=invid).last()
	inv.Invoice_Amount, inv.GST_Amount, inv.CESS_Amount = inv_amount, gst_amount, cess_amount
	inv.save()

	items = Copy_Billed_Items.objects.filter(Invoice_No__id=invid)
	inv_amount, gst_amount, cess_amount = 0, 0, 0
	for x in items:
		inv_amount = inv_amount + (x.Quantity*x.Unit_Price) + (x.Quantity*x.Unit_Price*x.GST/100)
		gst_amount = (gst_amount + (x.Quantity*x.Unit_Price*x.GST/100)) if x.GST else 0
		cess_amount = (cess_amount + (x.Quantity*x.Unit_Price*x.CESS/100)) if x.CESS else 0
	inv = Invoices.objects.filter(id=invid).last()
	inv.Invoice_Amount, inv.GST_Amount, inv.CESS_Amount = inv_amount, gst_amount, cess_amount
	inv.Due_Amount = inv.Invoice_Amount
	inv.save()

def inv_amount_exceed(request, rid):
	order = Orders.objects.filter(id=rid).last()
	invs = Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0)
	invs_sum=invs.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0 if invs != None else 0
	invs_sum = invs_sum
	if invs_sum >= order.Order_Value+10 or invs_sum >= order.Order_Value-10:
		# order.Can_Gen_Invoice=0
		order.save()
		return 1
	else:
		order.Can_Gen_Invoice=1
		order.save()
		return 0

def inv_amount_exceed_manual(request, rid, invamount):
	order = Orders.objects.filter(id=rid).last()
	invs = Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0)
	invs_sum=invs.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0 if invs != None else 0
	invs_sum = invs_sum + (invamount or 0)
	if invs_sum >= order.Order_Value+10 or invs_sum >= order.Order_Value-10:
		# order.Can_Gen_Invoice=0
		order.save()
		return 1
	else:
		order.Can_Gen_Invoice=1
		order.save()
		return 0

def postform(request, rid, invid, fnc):
	if request.method == 'POST':
		form = ManualInvoicesForm(request.POST, request.FILES) if fnc == 'create_manually' else ManualInvoicesForm(request.POST, request.FILES, instance=get_object_or_404(Invoices, id=invid))
		if form.is_valid():
			p = form.save(commit=False)
			if inv_amount_exceed_manual(request, rid, p.Invoice_Amount)==1:
				messages.error(request, 'Invoice generation not allowed due to all Invoices value under related received work order exceeding the order value')
				return 'orderslist'				
			else:
				p.save()				
				order = Orders.objects.get(id=rid)
				order.Billing_Status, order.Is_Billed = p, 1
				order.save()
				p.Billing_To, p.Order, p.Lock_Status, p.Is_Manual = order.Customer_Name, order, 1, 1
				p.save() 
				updateduedays(request, p.id)
				adjust_payments_to_invoices(request, order.id)
				return 'invlist'
	else:
		return 'getform'
