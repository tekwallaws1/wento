from datetime import date, datetime, timedelta 
from django.db.models import Sum, Avg, Count, F
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
	print(fd.Order_No)
	fd.save()


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
	# if invs_sum >= order.Order_Value+10:
	# 	# order.Can_Gen_Invoice=0
	# 	order.save()
	# 	return 1
	# else:
	# 	order.Can_Gen_Invoice=1
	# 	order.save()
	# 	return 0

def inv_amount_exceed_manual(request, rid, invamount):
	order = Orders.objects.filter(id=rid).last()
	invs = Invoices.objects.filter(Order=order, Lock_Status=1, Is_Proforma=0)
	invs_sum=invs.aggregate(sum=Sum('Invoice_Amount')).get('sum') or 0 if invs != None else 0
	# invs_sum = invs_sum + (invamount or 0)
	# if invs_sum >= order.Order_Value+10 or invs_sum >= order.Order_Value-10:
	# 	# order.Can_Gen_Invoice=0
	# 	order.save()
	# 	return 1
	# else:
	# 	order.Can_Gen_Invoice=1
	# 	order.save()
	# 	return 0

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
				p.Billing_To, p.Order, p.Lock_Status, p.Is_Manual, p.user, p.Billing_From = order.Customer_Name, order, 1, 1, Account.objects.get(user=request.user), order.RC
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

#######PAYMENTS UPDATES###########################################################################################################

def inv_due_agnst_pay(request, mode, pay_id):
	payment = Payment_Status.objects.get(id=pay_id)
	payment.user = Account.objects.get(user=request.user)
	payment.save()

	if payment.Invoice_No:
		inv = Invoices.objects.filter(Invoice_No=payment.Invoice_No.Invoice_No).last()
		if mode == 'edit':
			inv.Due_Amount = inv.Invoice_Amount
			inv.save()
			inv = Invoices.objects.filter(Invoice_No=payment.Invoice_No.Invoice_No).last()

		adjf = inv.Due_Amount - payment.Received_Amount
		dp, dn = 0, 0
		if adjf < 0:
			dn = -(adjf)
			if dn < 1 and dn >= 0:
				inv.Roundoff = adjf
				inv.save()
				dn = 0
		elif adjf > 0:
			dp = adjf
			if dp < 1 and dp >= 0:
				inv.Roundoff = dp
				inv.save()
				dp = 0
		else:
			pass
		
		if dp == 0 and dn == 0:
			inv.Due_Amount = 0
			inv.Payment_Cleared_Date = payment.Payment_Date
			inv.Payment_Status = payment
			inv.Final_Payment_Status = 1
			inv.save()
			po = Orders.objects.filter(Order_No=payment.Order_No.Order_No).last()
			po.Payment_Status = payment
			po.save()
			print('create 1')
			return 1
		elif dp > 0:
			inv.Due_Amount = inv.Due_Amount - payment.Received_Amount
			inv.Payment_Cleared_Date = None
			inv.Final_Payment_Status = 0
			inv.save()
			po = Orders.objects.filter(Order_No=payment.Order_No.Order_No).last()
			po.Payment_Status = payment
			po.save()
			print('2')
		elif dn > 0:
			inv.Due_Amount = 0
			inv.Payment_Cleared_Date = payment.Payment_Date
			inv.Payment_Status = payment
			inv.Final_Payment_Status = 1
			inv.save()
			po = Orders.objects.filter(Order_No=payment.Order_No.Order_No).last()
			po.Payment_Status = payment
			po.save()
			if mode == 'create':
				adj_invs_dues_p(request, payment, dn)
				print('ex')
		else:
			pass

		if mode == 'edit':
			print('edit')
			balance_inv_dues(request, payment.Order_No.Related_Project, payment.Order_No.Customer_Name, payment, inv.id)

	else:
		check_advance(request, mode, pay_id)


def check_advance(request, mode, pay_id):
	payment = Payment_Status.objects.get(id=pay_id)

	if payment.Order_No:
		inv = Invoices.objects.filter(Order=payment.Order_No)
		if inv:
			if inv.filter(Payment_Status__isnull=True):
				inv1 = inv.filter(Payment_Status__isnull=True).first()
				inv1.Payment_Status = payment
				inv1.save()
				payment.Invoice_No = inv1
				payment.save()
				inv_due_agnst_pay(request, mode, pay_id)
			else:
				inv1 = inv.filter(Due_Amount__gt=0).first()
				if inv1:
					inv1.Payment_Status = payment
					inv1.save()
					payment.Invoice_No = inv1
					payment.save()
					inv_due_agnst_pay(request, mode, pay_id)
		else: #Advnace
			payment.As_Advance_Amount = payment.Received_Amount
			payment.save()

def adj_invs_dues_p(request, payment, diff):
  customer = payment.Order_No.Customer_Name
  proj = payment.Order_No.Related_Project
  

  case1 = Invoices.objects.filter(Order=payment.Order_No, Due_Amount__gt=0, Order__Related_Project=proj).order_by('Invoice_Date')
  case2 = Invoices.objects.filter(Order__Customer_Name=customer, Lock_Status=1, Due_Amount__gt=0, Order__Related_Project=proj).order_by('Invoice_Date')
  
  diff = inv_adj(request, case1, diff, payment.id)
  if diff > 0:
  	diff = inv_adj(request, case2, diff, payment.id)
  case2.filter(Due_Amount__gt=0, Due_Amount__lt=1).update(Due_Amount=0, Roundoff=F('Due_Amount'))

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
				x.Roundoff = 0
				x.save()
			else:
				x.Due_Amount = x.Due_Amount - diff
				x.Payment_Cleared_Date = None
				x.Final_Payment_Status = 0
				x.Roundoff = 0
				x.save()
				diff = 0
	return diff

def balance_inv_dues(request, proj, customer, payment, exclude):
	invs = Invoices.objects.filter(Order__Customer_Name=customer, Lock_Status=1, Order__Customer_Name__Address_Type='Billing', Order__Related_Project=proj).order_by('Invoice_Date')
	pays = Payment_Status.objects.filter(Order_No__Customer_Name=customer, Order_No__Related_Project=proj).order_by('Payment_Date')
  
	invs_amnt = sum(invs.values_list('Invoice_Amount', flat=True))
	invs_due = sum(invs.values_list('Due_Amount', flat=True)) +  sum(invs.values_list('Roundoff', flat=True))
	pays_total = sum(pays.values_list('Received_Amount', flat=True))

	print(invs_due, invs_amnt - pays_total)

	if (invs_amnt == pays_total) or (invs_amnt < pays_total):
		Invoices.objects.filter(Order__Customer_Name=customer, Lock_Status=1, Due_Amount__gt=0, Order__Related_Project=proj).update(Due_Amount=0, Final_Payment_Status=1, Payment_Cleared_Date=payment.Payment_Date, Payment_Status=payment)
		print('all due set 0')
		return 3

	if invs_due == (invs_amnt - pays_total):
		print('all matched')
		return 4
	elif (invs_amnt - pays_total) > invs_due:
		diff = (invs_amnt - pays_total) - invs_due #it should be decrease from invs
		adj_invs_dues_n(request, payment, diff, exclude)
		print(diff, '5')
	else:
		diff = invs_due - (invs_amnt - pays_total)
		adj_invs_dues_p(request, payment, diff)
		print('6')

	Invoices.objects.filter(Order__Customer_Name=customer, Lock_Status=1, Due_Amount__gt=0, Due_Amount__lt=1).update(Due_Amount=0, Roundoff=F('Due_Amount'))


def adj_invs_dues_n(request, payment, diff, excludeid):
  customer = payment.Order_No.Customer_Name
  proj = payment.Order_No.Related_Project
  

  case1 = Invoices.objects.filter(Order=payment.Order_No, Due_Amount__gt=0, Order__Related_Project=proj).exclude(id=excludeid).order_by('Invoice_Date')
  case2 = Invoices.objects.filter(Order__Customer_Name=customer, Lock_Status=1, Due_Amount__gt=0, Order__Related_Project=proj).exclude(id=excludeid).order_by('Invoice_Date')

  case3 = Invoices.objects.filter(Order=payment.Order_No, Due_Amount=0, Order__Related_Project=proj).order_by('Invoice_Date')
  case4 = Invoices.objects.filter(Order__Customer_Name=customer, Lock_Status=1, Due_Amount=0, Order__Related_Project=proj).order_by('Invoice_Date')

  diff = inv_adj1(request, case1, diff)
  if diff > 0:
  	diff = inv_adj1(request, case2, diff)
  	if diff > 0:
  		diff = inv_adj1(request, case3, diff)
  		if diff > 0:
  			diff = inv_adj1(request, case4, diff)

  case2.filter(Due_Amount__gt=0, Due_Amount__lt=1).update(Due_Amount=0, Roundoff=F('Due_Amount'))

def paymentdelete(request, ordid, invid, dlt_amount):
	order = Orders.objects.get(id=ordid)
	inv =  Invoices.objects.filter(id=invid).last()
	proj = inv.Order.Related_Project
	

	inv_rec = inv.Invoice_Amount - inv.Due_Amount

	if dlt_amount >= inv_rec:
		dlt_amount = dlt_amount - inv_rec
		inv.Due_Amount = inv.Invoice_Amount
		inv.save()
		pm = Payment_Status.objects.filter(Invoice_No=inv)
		if pm:
			am = sum(pm.values_list('Received_Amount', flat=True))
			inv.Due_Amount = inv.Invoice_Amount - am
			if inv.Due_Amount < 0:
				inv.Due_Amount = 0
				inv.save()
				dlt_amount = dlt_amount + am
				print('dlt_amount',dlt_amount)
		else:
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
		case1 = Invoices.objects.filter(Order=order, Due_Amount__gt=0, Order__Related_Project=proj).exclude(id=inv.id).order_by('Invoice_Date')
		case2 = Invoices.objects.filter(Order__Customer_Name=order.Customer_Name, Lock_Status=1, Due_Amount__gt=0, Order__Related_Project=proj).exclude(id=inv.id).order_by('Invoice_Date')
		case3 = Invoices.objects.filter(Order=order, Due_Amount=0, Order__Related_Project=proj).order_by('Invoice_Date')
		case4 = Invoices.objects.filter(Order__Customer_Name=order.Customer_Name,  Lock_Status=1, Due_Amount=0, Order__Related_Project=proj).order_by('Invoice_Date')

		diff = dlt_amount
		diff = inv_adj1(request, case1, diff)
		if diff > 0:
			diff = inv_adj1(request, case2, diff)
			if diff > 0:
				diff = inv_adj1(request, case3, diff)
				if diff > 0:
					diff = inv_adj1(request, case4, diff)

		case2.filter(Due_Amount__gt=0, Due_Amount__lt=1).update(Due_Amount=0, Roundoff=F('Due_Amount'))
	
	pay = Payment_Status.objects.filter(Order_No=order).last()
	if pay:			
		inv_due_agnst_pay(request, 'edit', pay.id)
	else:
		pay = Payment_Status.objects.filter(Order_No__Customer_Name=order.Customer_Name, Order_No__Related_Project=proj).last()
		if pay:			
			inv_due_agnst_pay(request, 'edid', pay.id)

def inv_adj1(request, invs, diff):
	if invs != None:
		for x in invs:
			if diff >= (x.Invoice_Amount - x.Due_Amount):
				diff = diff - (x.Invoice_Amount - x.Due_Amount)
				x.Due_Amount = x.Invoice_Amount
				x.Payment_Status = None
				x.Payment_Cleared_Date = None
				x.Final_Payment_Status = 0
				x.Roundoff = 0
				x.save()
			else:
				x.Due_Amount = x.Due_Amount + diff
				x.Payment_Cleared_Date = None
				x.Final_Payment_Status = 0
				x.Roundoff = 0
				x.save()
				diff = 0
	return diff

def adjust_payments_to_invoices(request, ordid, invid):
	order = Orders.objects.get(id=ordid)
	customer = order.Customer_Name
	inv = Invoices.objects.filter(id=invid).last()
	inv.Due_Amount = inv.Invoice_Amount
	inv.Roundoff = 0
	inv.save()
	proj = inv.Order.Related_Project
	

	pays = Payment_Status.objects.filter(Invoice_No=inv)
	print('due', inv.Invoice_No, inv.Due_Amount)
	
	if pays:
		for x in pays:
			print(x.Received_Amount)
			inv_due_agnst_pay(request, 'create', x.id)
	else:
		case0 = Payment_Status.objects.filter(Invoice_No=inv).order_by('Payment_Date')
		case1 = Payment_Status.objects.filter(Order_No=order).order_by('Payment_Date')
		case2 = Payment_Status.objects.filter(Order_No__Customer_Name=customer, Order_No__Related_Project=proj).order_by('Payment_Date')

		if case1 == None and case2 == None and case0 == None:
			pass
		else:
			if case0:
				inv_due_agnst_pay(request, 'edit', case0.last().id)
			elif case1:
				inv_due_agnst_pay(request, 'edit', case1.last().id)
			else:
				if case2:
					inv_due_agnst_pay(request, 'edit', case2.last().id)


def balance_inv_dues1(request, customer):
	invs = Invoices.objects.filter(Order__Customer_Name=customer, Lock_Status=1, Order__Customer_Name__Address_Type='Billing').order_by('Invoice_Date')
	pays = Payment_Status.objects.filter(Order_No__Customer_Name=customer).order_by('Payment_Date')

	payment = Payment_Status.objects.filter(Order_No__Customer_Name=customer).last()

	if payment:
		invs_amnt = sum(invs.values_list('Invoice_Amount', flat=True))
		invs_due = sum(invs.values_list('Due_Amount', flat=True)) +  sum(invs.values_list('Roundoff', flat=True))
		pays_total = sum(pays.values_list('Received_Amount', flat=True))

		print(invs_due, invs_amnt - pays_total)

		if (invs_amnt == pays_total) or (invs_amnt < pays_total):
			Invoices.objects.filter(Order__Customer_Name=customer, Lock_Status=1, Due_Amount__gt=0).update(Due_Amount=0, Final_Payment_Status=1, Payment_Cleared_Date=payment.Payment_Date, Payment_Status=payment)
			print('all due set 0')
			return 3

		if invs_due == (invs_amnt - pays_total):
			print('all matched')
			return 4
		elif (invs_amnt - pays_total) > invs_due:
			diff = (invs_amnt - pays_total) - invs_due #it should be decrease from invs
			adj_invs_dues_n1(request,  diff)
			print(diff, '5')
		else:
			diff = invs_due - (invs_amnt - pays_total)
			case1 = Invoices.objects.filter(Order__Customer_Name=customer, Lock_Status=1, Due_Amount__gt=0).order_by('Invoice_Date')
			diff = inv_adj(request, case1, diff, payment.id)
			print('6')


def adj_invs_dues_n1(request, diff):
  customer = payment.Order_No.Customer_Name
  proj = payment.Order_No.Related_Project
  
  case1 = Invoices.objects.filter(Order__Customer_Name=customer, Lock_Status=1, Due_Amount__gt=0, Order__Related_Project=proj).order_by('Invoice_Date')
  case2 = Invoices.objects.filter(Order__Customer_Name=customer, Lock_Status=1, Due_Amount=0, Order__Related_Project=proj).order_by('Invoice_Date')

  diff = inv_adj1(request, case1, diff)
  if diff > 0:
  	diff = inv_adj1(request, case2, diff)
  case1.filter(Due_Amount__gt=0, Due_Amount__lt=1).update(Due_Amount=0, Roundoff=F('Due_Amount'))