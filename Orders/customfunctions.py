from datetime import date, datetime, timedelta 
from django.db.models import Sum, Avg, Count
from.models import *
from .forms import * 
from django.http import HttpResponse, JsonResponse
from Projects.fyear import get_financial_year, get_fy_date
from Projects.basedata import projectname, customer_updateledger
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


# def assign_paystatus_to_order(request, pay_id, order_id):
# 	order = Orders.objects.get(id=order_id)
# 	payment = Payment_Status.objects.get(id=pay_id)
# 	order.Payment_Status = payment
# 	order.save()

# 	if not payment.Order_No:
# 		payment.Order_No = order

# 	inv = Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0).order_by('Invoice_Date')
# 	payments  = Payment_Status.objects.filter(Order_No=order).order_by('Payment_Date')
# 	t_inv = sum(inv.values_list('Invoice_Amount', flat=True))
# 	t_pay = sum(payments.values_list('Received_Amount', flat=True))
# 	#here t_pay = total payment received except current payment, bcz pay_status not assigned to order

# 	if t_inv==0 and t_pay==0:
# 		payment.Payment_Type = 'Advance'

# 	elif t_inv - t_pay > 0:
# 		payment.Payment_Type = 'Due'
# 	else:
# 		payment.Payment_Type = 'Advance'

# 	payment.user = Account.objects.get(user=request.user)
# 	payment.save()

def assign_paystatus_to_order(request, pay_id):
  payment = Payment_Status.objects.get(id=pay_id)
  payment.user = Account.objects.get(user=request.user)
  payment.save()
  
  if not payment.Order_No:
  	po_no = payment.Invoice_No.Order_No
  	payment.Order_No = po_no
  	payment.save()
  else:
  	if payment.Invoice_No:
	  	inv = Invoices.objects.filter(Invoice_No=payment.Invoice_No.Invoice_No).last()
	  	inv.Payment_Status = payment
	  	inv.save()
	  	payment = Payment_Status.objects.get(id=pay_id)
	  	inv_rec = sum(Payment_Status.objects.filter(Invoice_No=payment.Invoice_No).values_list('Received_Amount', flat=True))
  		if inv.Due_Amount <= inv_rec:
	  		inv.Due_Amount = 0
	  		inv.Payment_Cleared_Date = payment.Payment_Date
	  		inv.Final_Payment_Status = 1
	  		inv.save()
	  	else:
	  		inv.Due_Amount = inv.Due_Amount - inv_rec
	  		inv.Payment_Cleared_Date = None
	  		inv.Final_Payment_Status = 0
	  		inv.save()
  
  po = Orders.objects.filter(Order_No=payment.Order_No.Order_No).last()
  po.Payment_Status = payment
  po.save()

  payment = Payment_Status.objects.get(id=pay_id)
  customer = payment.Order_No.Customer_Name

  invs = Invoices.objects.filter(Order__Customer_Name=customer).order_by('Invoice_Date')
  pays = Payment_Status.objects.filter(Order_No__Customer_Name=customer).order_by('Payment_Date')
  
  invs_amnt = sum(invs.values_list('Invoice_Amount', flat=True))
  invs_due = sum(invs.values_list('Due_Amount', flat=True))
  pays_total = sum(pays.values_list('Received_Amount', flat=True))

  due = invs_amnt - pays_total
  case1 = Invoices.objects.filter(Order=payment.Order_No, Due_Amount__gt=0).order_by('Invoice_Date')
  case2 = Invoices.objects.filter(Order__Customer_Name=customer, Due_Amount__gt=0).order_by('Invoice_Date')

  case3 = Invoices.objects.filter(Order=payment.Order_No, Due_Amount=0).order_by('Invoice_Date')
  case4 = Invoices.objects.filter(Order__Customer_Name=customer, Due_Amount=0).order_by('Invoice_Date')

  if due > 0:
  	if due != invs_due:
  		diff = invs_due - due 
	  	if diff > 0: # if it is positive diff  deduct from other invoices i.e decrease due amount
	  		diff = inv_adj(request, case1, diff, pay_id)
	  		if diff > 0:
	  			diff = inv_adj(request, case2, diff, pay_id)
		  	# if still duff > 0, its remains as advance
	  	elif diff < 0: # increase due amount
	  		diff = -(diff)
	  		diff = inv_adj1(request, case1, diff)
	  		if diff > 0:
	  			diff = inv_adj1(request, case2, diff)
	  			if diff > 0:
	  				diff = inv_adj1(request, case3, diff)
	  				if diff > 0:
	  					diff = inv_adj1(request, case4, diff)
  elif due == 0:
  	pass
  else:
  	Invoices.objects.filter(Order__Customer_Name=customer, Due_Amount__gt=0).update(Due_Amount=0, Final_Payment_Status=1, Payment_Cleared_Date=payment.Payment_Date, Payment_Status=payment)

def paymentdelete(request, ordid, invid, dlt_amount):
	order = Orders.objects.get(id=ordid)
	inv =  Invoices.objects.filter(id=invid).last()

	inv_rec = inv.Invoice_Amount - inv.Due_Amount
	
	if dlt_amount >= inv_rec:
		dlt_amount = dlt_amount - inv_rec
		inv.Due_Amount = inv.Invoice_Amount
		inv.Payment_Cleared_Date = None
		inv.Final_Payment_Status = 0
		inv.Payment_Status = None
		inv.save()
	else:
		inv.Due_Amount = inv.Invoice_Amount - (inv_rec - dlt_amount)
		inv.Payment_Cleared_Date = None
		inv.Final_Payment_Status = 0
		inv.save()
		dlt_amount = 0
	
	if dlt_amount > 0:
		case1 = Invoices.objects.filter(Order=order, Due_Amount__gt=0).order_by('Invoice_Date')
		case2 = Invoices.objects.filter(Order__Customer_Name=order.Customer_Name, Due_Amount__gt=0).order_by('Invoice_Date')
		case3 = Invoices.objects.filter(Order=order, Due_Amount=0).order_by('Invoice_Date')
		case4 = Invoices.objects.filter(Order__Customer_Name=order.Customer_Name, Due_Amount=0).order_by('Invoice_Date')

		diff = dlt_amount

		diff = inv_adj1(request, case1, diff)
		if diff > 0:
			diff = inv_adj1(request, case2, diff)
			if diff > 0:
				diff = inv_adj1(request, case3, diff)
				if diff > 0:
					diff = inv_adj1(request, case4, diff)
	
	pay = Payment_Status.objects.filter(Order_No=order).last()
	if pay:			
		assign_paystatus_to_order(request, pay.id)
	else:
		pay = Payment_Status.objects.filter(Order_No__Customer_Name=order.Customer_Name).last()
		if pay:			
			assign_paystatus_to_order(request, pay.id)

def inv_adj(request, invs, diff, pay_id):
	if invs != None:
		payment = Payment_Status.objects.get(id=pay_id)
		for x in invs:
			if x.Due_Amount <= diff:
				diff = diff - x.Due_Amount
				x.Due_Amount = 0
				x.Payment_Status = payment
				x.Payment_Cleared_Date = payment.Payment_Date
				x.Final_Payment_Status = 1
				x.save()
			else:
				x.Due_Amount = x.Due_Amount - diff
				x.Payment_Cleared_Date = None
				x.Final_Payment_Status = 0
				x.save()
				diff = 0
	return diff

def inv_adj1(request, invs, diff):
	if invs != None:
		for x in invs:
			if diff >= (x.Invoice_Amount - x.Due_Amount):
				diff = diff - (x.Invoice_Amount - x.Due_Amount)
				x.Due_Amount = x.Invoice_Amount
				x.Payment_Status = None
				x.Payment_Cleared_Date = None
				x.Final_Payment_Status = 0
				x.save()
			else:
				x.Due_Amount = x.Due_Amount + diff
				x.Payment_Cleared_Date = None
				x.Final_Payment_Status = 0
				x.save()
				diff = 0
	return diff


def adjust_payments_to_invoices(request, ordid, invid):
	order = Orders.objects.get(id=ordid)
	customer = order.Customer_Name
	inv = Invoices.objects.filter(id=invid).last()
	inv.Due_Amount = inv.Invoice_Amount
	inv.save()
	inv = Invoices.objects.filter(id=invid).last()

	if Payment_Status.objects.filter(Invoice_No=inv):
		assign_paystatus_to_order(request, Payment_Status.objects.filter(Invoice_No=inv).last().id)
	else:
		case1 = Payment_Status.objects.filter(Order_No=order).order_by('Payment_Date')
		case2 = Payment_Status.objects.filter(Order_No__Customer_Name=customer).order_by('Payment_Date')

		if case1 == None and case2 == None:
			pass
		else:
			if case1:
				assign_paystatus_to_order(request, case1.last().id)
			else:
				if case2:
					assign_paystatus_to_order(request, case2.last().id)

# def adjust_payments_to_invoices(request, orderid):
# 	# if invoice lock and if any payments under this order before invoice gen.
# 	# inv_current = Invoices.objects.filter(id=invid).last()
# 	order = Orders.objects.get(id=orderid)
# 	inv = Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0).order_by('Invoice_Date')
# 	payments  = Payment_Status.objects.filter(Order_No=order).order_by('Payment_Date')
# 	t_inv = inv.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0 if inv != None else 0
# 	t_pay = payments.aggregate(sum=Sum('Received_Amount')).get('sum') or 0 if payments != None else 0
	

# 	# CASE-1: No Prev Invoices, No Payments (only cureent gen invoice)
# 	if len(inv) == 1 and t_pay==0:
# 		for x in inv:
# 			x.Due_Amount = x.Invoice_Amount
# 			x.save()
# 		return 1

# 	# CASE-2: Previous invoices available against that order but no payments gainst order
# 	if len(inv) > 1 and t_pay==0:
# 		for x in inv:
# 			x.Due_Amount = x.Invoice_Amount
# 			x.save()
# 		print('return 1')
# 		return 2

# 	# CASE-3: Invoices Due Amount Adjustments Against Order and Received Paymants
# 	if t_inv+10 <= t_pay or t_inv-10 <= t_pay:
# 		# if total billing value =< total received value update all bills due as 0
# 		Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0).update(Due_Amount=0)
# 		print('return 3')
# 		return 3
# 	else:
# 		for x in inv:
# 			if t_pay > x.Invoice_Amount:
# 				x.Due_Amount = 0
# 				x.save()
# 				t_pay = t_pay - x.Invoice_Amount
# 				print('return tpay', x, t_pay)
# 			else:
# 				# means whole received payment is less than one single invoice amount
# 				x.Due_Amount = x.Invoice_Amount - t_pay
# 				t_pay = 0
# 				x.save()
# 				print('return 4')
# 				# Breaking for and while loops
# 		return 4

def adj_pay_to_all_inv(request, customer):
	pays = Payment_Status.objects.filter(Order_No__Customer_Name=customer).order_by('Payment_Date')
	# pays_total = sum(pays.values_list('Received_Amount', flat=True))

	# invs = Invoices.objects.filter(Order__Customer_Name=customer).order_by('Invoice_Date')
	# for x in invs:
	# 	if pays_total >= x.Invoice_Amount:
	# 		pays_total = pays_total - x.Invoice_Amount
	# 		x.Due_Amount = 0
	# 		x.Final_Payment_Status = 1
	# 		# x.Payment_Cleared_Date = pays.last().Payment_Date
	# 		# Purchases.objects.filter(PO_No=x.PO_No.PO_No).update(Payment_Status=pays.last())
	# 		# x.Payment_Status = pays.last()
	# 		x.save()
	# 	else:
	# 		if pays_total > 0:
	# 			x.Due_Amount = x.Invoice_Amount - pays_total
	# 			# x.Payment_Status = pays.last()
	# 			# Purchases.objects.filter(PO_No=x.PO_No.PO_No).update(Payment_Status=pays.last())
	# 			pays_total = 0
	# 			x.save()
	# 		else:
	# 			x.Due_Amount = x.Invoice_Amount
	# 			x.save()


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
	
	# fd.Invoice_No_Format = No_Formats.objects.filter(No_Format_Related_To='Invoice').last()
	# fd.Invoice_No = str(fd.Invoice_No_Format.No_Format)+str(fd.FY)+'/'+str(invno1)
	fd.Invoice_No = str(fd.FY)+'/'+str(invno1)
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
	if invs_sum >= order.Order_Value+10:
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
				adjust_payments_to_invoices(request, order.id, p.id)
				pdata = projectname(request, Projects.objects.filter(Short_Name = order.Related_Project.Short_Name).last().Short_Name)
				if fnc == 'create_manually':
					customer_updateledger(request, 'custinv', 'create', pdata, Invoices.objects.get(id=p.id))
				else:
					customer_updateledger(request, 'custinv', 'edit', pdata, Invoices.objects.get(id=p.id))
				return 'invlist'
	else:
		return 'getform'
