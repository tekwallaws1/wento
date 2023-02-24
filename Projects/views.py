from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q
from .models import *
from .forms import *
from .filters import * 
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import date, datetime, timedelta 
from django.db.models import Sum, Avg, Count
from django.contrib.auth.decorators import login_required
from UserAccounts.models import *
from Orders.models import *
from Products.models import *
from Debits.models import * 
from .basedata import projectname, projectname1, firmname, customer_updateledger, vendor_updateledger, permissions
from .fyear import fyr

@login_required
def Select_Firm(request):
	firm = firmname(request, None)
	if len(firm['fm']) == 1:
		fm = CompanyDetails.objects.filter(ds=True, Status=1).last()
		pdata = projectname1(request, None, fm)
		return render(request, 'projects/SelectProject.html', {'pdata':pdata, 'firm':fm.Short_Name})

	return render(request, 'projects/SelectFirm.html', {'firm':firm})
	# return render(request, 'proposals/ContactUs.html', {'pdata':pdata})


@login_required
def Select_Project(request, firm):
	fm = CompanyDetails.objects.filter(Short_Name=firm).last()
	pdata = projectname1(request, None, fm)
	return render(request, 'projects/SelectProject.html', {'pdata':pdata, 'firm':firm})
	# return render(request, 'proposals/ContactUs.html', {'pdata':pdata})

@login_required
def Select_Module(request, firm, proj):
	print(proj)
	pdata = projectname(request, proj)
	print(pdata)
	return render(request, 'projects/SelectModule.html', {'pdata':pdata, 'firm':firm})

@login_required
def CustDt_Form(request, firm, proj, fnc, rid):
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(CustDt, id=rid)
			form = CustomerForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				p = form.save()
				p.State_Code = p.GST_No[0:2] if p.GST_No != None else None
				p.save()
				messages.success(request, "Selected Customer Details Has Been Updated")
				url = '/'+str(firm)+'/'+str(pdata['pj'])+'/customerslist/OneTime/'
				return redirect(url)
			else:
				return render(request, 'projects/CustDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			getdata = get_object_or_404(CustDt, id=rid)
			form = CustomerForm(instance=getdata)
			return render(request, 'projects/CustDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(CustDt, id=rid)
		orders = Orders.objects.filter(Customer_Name__id=rid)
		ship = Invoices.objects.filter(Lock_Status=1, Shipping_To__id=rid)
		if orders or ship:
			messages.error(request, "Due to Orders linked with this customer you can not delete this customer. Instaed of delete, you can make it hide by unmark in edit options")
		else:
			getdata.delete()
			messages.success(request, "Selected Customer Details Has Been Deleted")
		url = '/'+str(firm)+'/'+str(pdata['pj'])+'/customerslist/OneTime/'
		return redirect(url)

	if request.method ==  'POST': #Create
		form = CustomerForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			p.State_Code = p.GST_No[0:2] if p.GST_No != None else None
			p.RC = CompanyDetails.objects.filter(Short_Name=firm).last()
			p.Related_Project = Projects.objects.filter(Short_Name=proj).last()
			p.save()
			messages.success(request, "Customer Details Has Been Added")
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/customerslist/OneTime/'
			return redirect(url)
		else:
			return render(request, 'projects/CustDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(CustDt, id=rid)
			form = CustomerForm(instance=getdata)
			return render(request, 'projects/CustDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			form = CustomerForm()
			return render(request, 'projects/CustDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

@login_required
def CustDt_List(request, firm, proj, mode):
	pdata = projectname(request, proj)
	plj = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	contact_person = []
	if mode != 'Inactive':
		table = CustDt.objects.filter(Status=1, RC__Short_Name=firm, Customer_Type='Regular Customer', **plj) if mode == 'Regular' else CustDt.objects.filter(Status=1, RC__Short_Name=firm, Customer_Type='One Time Customer', **plj) 
	else:
		table = CustDt.objects.filter(Status=0, RC__Short_Name=firm, **plj)
	filter_data = CustomerFilter(request.GET, queryset=table)
	table = filter_data.qs
	for x in table:
		p = CustContDt.objects.filter(Customer_Name=x, ds=1)
		contact_person.append(p if p else None)
	data = zip(table, contact_person)
	return render(request, 'projects/CustDtList.html', {'data':data, 'filter_data':filter_data, 'pdata':pdata, 'firm':firm, 'mode':mode})

@login_required
def CustContDt_Form(request, firm, proj, fnc, rid):
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(CustContDt, id=rid)
			form = CustomerContactForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				form.save()
				messages.success(request, "Selected Customer Contact Details Has Been Updated")
				url = '/'+str(firm)+'/'+str(pdata['pj'])+'/customerslist/OneTime/'
				return redirect(url)
			else:
				return render(request, 'projects/CustContDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			getdata = get_object_or_404(CustContDt, id=rid)
			form = CustomerContactForm(instance=getdata)
			return render(request, 'projects/CustContDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(CustContDt, id=rid)
		orders = Orders.objects.filter(Order_Reference_Person__id=rid)
		if orders:
			getdata.delete()
			messages.success(request, "Selected Customer Contact Details Has Been Deleted")
		else:
			getdata.ds = 0
			getdata.save()
			messages.success(request, "Selected Customer Contact Details Has Been Send to Recyclebin")
		url = '/'+str(firm)+'/'+str(pdata['pj'])+'/customerslist/OneTime/'
		return redirect(url)

	if request.method ==  'POST': #Create
		form = CustomerContactForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			p.Customer_Name = CustDt.objects.get(id=rid)
			p.save()
			messages.success(request, "Customer Contact Details Has Been Added")
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/customerslist/OneTime/'
			return redirect(url)
		else:
			return render(request, 'projects/CustContDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(CustContDt, id=rid)
			form = CustomerContactForm(instance=getdata)
			return render(request, 'projects/CustContDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			form = CustomerContactForm()
			return render(request, 'projects/CustContDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})


@login_required
def VendDt_Form(request, firm, proj, fnc, rid):
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(VendDt, id=rid)
			form = VendorForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				p = form.save()
				p.State_Code = p.GST_No[0:2] if p.GST_No != None else None
				p.save()
				messages.success(request, "Selected Supplier/Vendor Details Has Been Updated")
				url = '/'+str(firm)+'/'+str(pdata['pj'])+'/vendorslist/'
				return redirect(url)
			else:
				return render(request, 'projects/VendDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			getdata = get_object_or_404(VendDt, id=rid)
			form = VendorForm(instance=getdata)
			return render(request, 'projects/VendDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(VendDt, id=rid)
		pos = Purchases.objects.filter(Vendor__id=rid)
		if pos:
			messages.error(request, "Due to Purchases linked with this vendor you can not delete this vendor. Instaed of delete, you can make it hide by unmark in edit options")
		else:
			getdata.delete()
			messages.success(request, "Selected Supplier/Vendor Details Has Been Deleted")
		url = '/'+str(firm)+'/'+str(pdata['pj'])+'/vendorslist/'
		return redirect(url)

	if request.method ==  'POST': #Create
		form = VendorForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			p.State_Code = p.GST_No[0:2] if p.GST_No != None else None
			p.RC = CompanyDetails.objects.filter(Short_Name=firm).last()
			p.save()
			messages.success(request, "Supplier/Vendor Details Has Been Added")
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/vendorslist/'
			return redirect(url)
		else:
			return render(request, 'projects/VendDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(VendDt, id=rid)
			form = VendorForm(instance=getdata)
			return render(request, 'projects/VendDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			form = VendorForm()
			return render(request, 'projects/VendDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

@login_required
def VendDt_List(request, firm, proj):
	pdata = projectname(request, proj)
	contact_person = []
	table = VendDt.objects.filter(ds=1, RC__Short_Name=firm)
	filter_data = VendorFilter(request.GET, queryset=table)
	table = filter_data.qs
	for x in table:
		p = VendContDt.objects.filter(Supplier_Name=x, ds=1)
		contact_person.append(p if p else None)
	data = zip(table, contact_person)
	return render(request, 'projects/VendDtList.html', {'data':data, 'filter_data':filter_data, 'pdata':pdata, 'firm':firm})

@login_required
def VendContDt_Form(request, firm, proj, fnc, rid):
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(VendContDt, id=rid)
			form = VendorContactForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				form.save()
				messages.success(request, "Selected Supplier/Vendor Contact Details Has Been Updated")
				url = '/'+str(firm)+'/'+str(pdata['pj'])+'/vendorslist/'
				return redirect(url)
			else:
				return render(request, 'projects/VendContDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			getdata = get_object_or_404(VendContDt, id=rid)
			form = VendorContactForm(instance=getdata)
			return render(request, 'projects/VendContDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(VendContDt, id=rid)
		pos = Purchases.objects.filter(Vendor_Contact__id=rid)
		if pos:
			getdata.ds = 0
			getdata.save()
			messages.success(request, "Selected Supplier/Vendor Contact Details Has Been Send to Recyclebin")
		else:
			getdata.delete()
			messages.success(request, "Selected Supplier/Vendor Details Has Been Deleted")					
		url = '/'+str(firm)+'/'+str(pdata['pj'])+'/vendorslist/'
		return redirect(url)

	if request.method ==  'POST': #Create
		form = VendorContactForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			p.Supplier_Name = VendDt.objects.get(id=rid)
			p.save()
			messages.success(request, "Supplier/Vendor Contact Details Has Been Added")
			url = '/'+str(firm)+'/'+str(pdata['pj'])+'/vendorslist/'
			return redirect(url)
		else:
			return render(request, 'projects/VendContDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(VendContDt, id=rid)
			form = VendorContactForm(instance=getdata)
			return render(request, 'projects/VendContDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			form = VendorContactForm()
			return render(request, 'projects/VendContDtForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

@login_required
def Company_Form(request, firm, proj, fnc, rid):
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #update
		if request.method ==  'POST':
			getdata = get_object_or_404(CompanyDetails, id=rid)
			form = CompanyForm(request.POST, request.FILES, instance=getdata)
			if form.is_valid():
				p = form.save()
				p.State_Code = p.GST_No[0:2] if p.GST_No != None else None
				p.save()
				messages.success(request, "Selected Company Details Has Been Updated")
				url = '/'+str(firm)+'/'+str(pdata['pj'])+'/companylist/'
				return redirect(url)
			else:
				return render(request, 'projects/CompanyDetailsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			getdata = get_object_or_404(CompanyDetails, id=rid)
			form = CompanyForm(instance=getdata)
			return render(request, 'projects/CompanyDetailsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

	elif fnc == 'delete': #Delete
		getdata = get_object_or_404(CompanyDetails, id=rid)
		orders = Orders.objects.filter(RC__id=rid)
		pos = Purchases.objects.filter(RC__id=rid)
		if orders or pos:
			messages.error(request, "Due to Orders/Purchases linked with this, you can not delete this. Instaed of delete, you can make it hide by unmark in edit options")
		else:
			getdata.delete()
		messages.success(request, "Selected Company Details Has Been Send to Recyclebin")
		url = '/'+firm+'/'+pdata['pj']+'/companylist/'
		return redirect(url)

	if request.method ==  'POST': #Create
		form = CompanyForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save()
			p.State_Code = p.GST_No[0:2] if p.GST_No != None else None
			p.save()
			messages.success(request, "Company Details Has Been Added")
			url = '/'+firm+'/'+pdata['pj']+'/companylist/'
			return redirect(url)
		else:
			return render(request, 'projects/CompanyDetailsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
	else:
		if fnc == 'copy':
			getdata = get_object_or_404(CompanyDetails, id=rid)
			form = CompanyForm(instance=getdata)
			return render(request, 'projects/CompanyDetailsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})
		else:
			form = CompanyForm()
			return render(request, 'projects/CompanyDetailsForm.html', {'form': form, 'pdata':pdata, 'firm':firm})

@login_required
def Companies_List(request, firm, proj):
	pdata = projectname(request, proj)
	table = CompanyDetails.objects.filter(ds=1)
	return render(request, 'projects/CompanyDetails.html', {'table':table, 'pdata':pdata, 'firm':firm})


@login_required
def GST_Returns(request, firm, proj, cat, months):
	pdata = projectname(request, proj)
	mnth = date.today() if months == 'month' else (datetime.strptime(months, '%Y-%m'))
	months = mnth
	mnth = months.month

	inputgst  = Vendor_Invoices.objects.filter(Invoice_Date__month=mnth, GST_Amount__isnull=False, PO_No__RC__Short_Name=firm).order_by('Invoice_No')
	outputgst = Invoices.objects.filter(Invoice_Date__month=mnth, Lock_Status=1, Set_For_Returns=1, GST_Amount__isnull=False, Order__RC__Short_Name=firm).order_by('Invoice_No')

	Ival, Oval, Igst, Ogst, Ocgst, Osgst, Oigst = [],[],[],[],[],[],[]
	ic, oc, It_gst, Ot_gst, Ot_cgst, Ot_sgst, Ot_igst = 0,0,0,0,0,0,0
	cust_bil = sum(outputgst.values_list('Invoice_Amount',flat=True)) if outputgst != None else 0
	vend_bil = sum(inputgst.values_list('Invoice_Amount',flat=True)) if inputgst != None else 0
	ic, oc = len(inputgst) or 0, len(outputgst) or 0
	# It_gst, Ot_gst = sum(inputgst.values_list('GST_Amount', flat=True)) or 0, sum(outputgst.values_list('GST_Amount', flat=True)) or 0
	
	for x in inputgst:
		Igst.append(x.GST_Amount)
		Ival.append(x.Invoice_Amount-x.GST_Amount)
	for x in outputgst:
		Oval.append(x.Invoice_Amount-x.GST_Amount)
		if x.Billing_To.State == x.Billing_From.State:
			Ogst.append(x.GST_Amount)
			Ocgst.append(x.GST_Amount/2)
			Osgst.append(x.GST_Amount/2)
			Oigst.append(0)
		else:
			Ogst.append(x.GST_Amount) 
			Ocgst.append(0)
			Osgst.append(0)
			Oigst.append(x.GST_Amount)

	It_gst, Ot_gst, Ot_cgst, Ot_sgst, Ot_igst = sum(Igst), sum(Ogst), sum(Ocgst), sum(Osgst), sum(Oigst)
	input_gst = zip(inputgst, Ival, Igst)
	output_gst = zip(outputgst, Oval, Ogst, Ocgst, Osgst, Oigst)
	gstcredit = sum(Vendor_Invoices.objects.filter(Invoice_Date__month__lte=mnth, GST_Amount__isnull=False, PO_No__RC__Short_Name=firm).values_list('GST_Amount', flat=True)) - sum(Invoices.objects.filter(Lock_Status=1, Set_For_Returns=1, Invoice_Date__month__lte=mnth, GST_Amount__isnull=False, Order__RC__Short_Name=firm).values_list('GST_Amount', flat=True))
	gstcredit = 0 if gstcredit < 0 else gstcredit
	gst = {'ic':ic, 'oc':oc, 'It_gst':It_gst, 'Ot_gst':Ot_gst, 'Ot_cgst':Ot_cgst, 'Ot_sgst':Ot_sgst, 'Ot_igst':Ot_igst, 'gstcredit':gstcredit}

	return render(request, 'projects/gst.html', {'pdata':pdata, 'firm':firm, 'input_gst':input_gst, 'output_gst':output_gst, 'gst':gst, 'cat':cat, 'month':months, 'cust_bil':cust_bil, 'vend_bil':vend_bil})


@login_required
def Cust_Ledger(request, firm, proj, mode):
	
	# Customer_Ledger.objects.filter(RC__Short_Name=firm).delete()
	# invs = Invoices.objects.filter(Lock_Status=1, Order__RC__Short_Name=firm)
	# for x in invs:
	# 	pdata = projectname(request, x.Order.Related_Project.Short_Name)
	# 	customer_updateledger(request, 'custinv', 'create', pdata, x)
	# return HttpResponse('hi')
	
	# pays = Payment_Status.objects.filter(Order_No__RC__Short_Name=firm)
	# for x in pays:
	# 	pdata = projectname(request, x.Order_No.Related_Project.Short_Name)
	# 	customer_updateledger(request, 'custpay', 'create', pdata, x)
	# return HttpResponse('hi')
	
	pdata = projectname(request, proj)
	# lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	table = Customer_Ledger.objects.filter(RC__Short_Name=firm).order_by('Sr_No')
	filter_data = CustomerLedgerFilter(request.GET, queryset=table)
	table = filter_data.qs
	if filter_data.form.cleaned_data.get('customer'):
		custflt = filter_data.form.cleaned_data.get('customer')
	else:
		custflt = 0
	cust = CustDt.objects.filter(Address_Type='Billing', Status=1, ds=1, Short_Name=firm)
	return render(request, 'projects/CustomerLedger.html', {'pdata':pdata, 'firm':firm, 'table':table, 'filter_data':filter_data, 'custflt':custflt, 'cust':cust})


@login_required
def Vend_Ledger(request, firm, proj, mode):

	# Vendor_Ledger.objects.filter(RC__Short_Name=firm).delete()
	# invs = Vendor_Invoices.objects.filter(PO_No__RC__Short_Name=firm)
	# for x in invs:
	# 	pdata = projectname(request, x.PO_No.Related_Project.Short_Name)
	# 	vendor_updateledger(request, 'vendinv', 'create', pdata, x)
	# return HttpResponse('hi')
	
	# pays = Vendor_Payment_Status.objects.filter(PO_No__RC__Short_Name=firm)
	# for x in pays:
	# 	pdata = projectname(request, x.PO_No.Related_Project.Short_Name)
	# 	vendor_updateledger(request, 'vendpay', 'create', pdata, x)
	# return HttpResponse('hi')
	
	pdata = projectname(request, proj)
	# lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	table = Vendor_Ledger.objects.filter(RC__Short_Name=firm).order_by('Sr_No')
	filter_data = VendorLedgerFilter(request.GET, queryset=table)
	table = filter_data.qs
	if filter_data.form.cleaned_data.get('vendor'):
		vendflt = filter_data.form.cleaned_data.get('vendor')
	else:
		vendflt = 0
	vend = VendDt.objects.filter(Status=1, ds=1, RC__Short_Name=firm)
	return render(request, 'projects/VendorLedger.html', {'pdata':pdata, 'firm':firm, 'table':table, 'filter_data':filter_data, 'vendflt':vendflt, 'vend':vend})


@login_required
def Daily_Finance(request, firm, proj, dur, status):	
	# if permissions(request, 'Received Orders Dashboard', 'View', firm, proj, Account.objects.get(user=request.user)) != 1: return HttpResponse(na_message) 
	pdata = projectname(request, proj)
	pjl1 = {'Order_No__Related_Project__isnull':False} if proj == 'All' else {'Order_No__Related_Project':pdata['pj']}
	pjl2 = {'PO_No__Related_Project__isnull':False} if proj == 'All' else {'PO_No__Related_Project':pdata['pj']}
	pjl3 = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	
	usr = Account.objects.get(user=request.user)
	if usr.Only_Their_Works == 1:
		pjl1 = {'Order_No__Related_Project__isnull':False, 'Order_No__user':usr} if proj == 'All' else {'Order_No__Related_Project':pdata['pj'], 'Order_No__user':usr}
		pjl2 = {'PO_No__Related_Project__isnull':False, 'user':usr} if proj == 'All' else {'PO_No__Related_Project':pdata['pj'], 'user':usr}
		pjl3 = {'Related_Project__isnull':False, 'Employ':usr} if proj == 'All' else {'Related_Project':pdata['pj'], 'Employ':usr}

	fltbnk = None
	if not request.GET:
		if dur == 'today':
			sDate, eDate = date.today(), date.today()
		elif dur == 'Yesterday':
			sDate, eDate = date.today() - timedelta(days=1), date.today() - timedelta(days=1)
		elif dur == 'Week':
			weekday = date.today().weekday()
			sDate, eDate = date.today() - timedelta(days=weekday), date.today()
		elif dur == 'Month':
			sDate, eDate = date(date.today().year, date.today().month, 1), date.today()
		elif dur == 'Year':
			sDate, eDate = fyr(), date.today()
		elif dur == 'All':
			sDate, eDate = date(2000, 4, 1), date.today()
	else:
		if request.GET["bnk"]:
			fltbnk = request.GET["bnk"]

		if request.GET["from_date"] and request.GET["to_date"] :
			sDate, eDate = datetime.strptime(request.GET["from_date"], "%Y-%m-%d").date(), datetime.strptime(request.GET["to_date"], "%Y-%m-%d").date()
		elif not request.GET["from_date"] and request.GET["to_date"]:
			sDate, eDate = datetime.strptime(request.GET["to_date"], "%Y-%m-%d").date(), datetime.strptime(request.GET["to_date"], "%Y-%m-%d").date()
		elif request.GET["from_date"] and not request.GET["to_date"]:
			sDate, eDate = datetime.strptime(request.GET["from_date"], "%Y-%m-%d").date(), datetime.strptime(request.GET["from_date"], "%Y-%m-%d").date()
		else:
			if not request.GET["bnk"]:
				return HttpResponse('Error: Please Submit Valid Data')
			else:
				sDate, eDate = date.today(), date.today()


	sales = Payment_Status.objects.filter(Order_No__RC__Short_Name=firm,  Payment_Date__date__gte=sDate, Payment_Date__date__lte=eDate).order_by('Payment_Date')
	purch = Vendor_Payment_Status.objects.filter(PO_No__RC__Short_Name=firm,  Payment_Date__date__gte=sDate, Payment_Date__date__lte=eDate).order_by('Payment_Date')
	exp = Debit_Amounts.objects.filter(RC__Short_Name=firm,  Issued_Date__gte=sDate, Issued_Date__lte=eDate).order_by('Issued_Date')
	
	if fltbnk != None:
		sales = sales.filter(Account_Name__id=fltbnk)
		purch = purch.filter(Account_Name__id=fltbnk)
		exp = exp.filter(Account_Name__id=fltbnk)


	dates, cat, receipt = [], [], []
	sl, pr, ex = [], [], []

	dates_list = list(dict.fromkeys([d.date() for d in list(sales.values_list('Payment_Date', flat=True))] + [d.date() for d in list(purch.values_list('Payment_Date', flat=True))] + list(exp.values_list('Issued_Date', flat=True))))
	dates_list.sort(reverse=True)

	for x in dates_list:
		if sales.filter(Payment_Date__date=x):
			for a in sales.filter(Payment_Date__date=x):
				receipt.append(a)
				cat.append('Received')
		if purch.filter(Payment_Date__date=x):
			for b in purch.filter(Payment_Date__date=x):
				receipt.append(b)
				cat.append('Paid')
		if exp.filter(Issued_Date=x):
			for c in exp.filter(Issued_Date=x):
				receipt.append(c)
				cat.append('Expenses')

	tsales = sum(sales.values_list('Received_Amount', flat=True)) if sales != None else 0
	tpurch = sum(purch.values_list('Paid_Amount', flat=True)) if sales != None else 0
	texp = sum(exp.values_list('Issued_Amount', flat=True)) if sales != None else 0
	
	if sales:
		c_upi = sum(sales.filter(Account_Name__Account_Type='UPI').values_list('Received_Amount', flat=True)) if sales.filter(Account_Name__Account_Type='UPI') != None else 0
		c_bank = sum(sales.filter(Account_Name__Account_Type='Company').values_list('Received_Amount', flat=True)) if sales.filter(Account_Name__Account_Type='Company') != None else 0
		c_cash = sum(sales.filter(Account_Name__Account_Type='CASH').values_list('Received_Amount', flat=True)) if sales.filter(Account_Name__Account_Type='CASH') != None else 0
	else:
		c_upi, c_bank, c_cash = 0, 0, 0

	if purch:
		dp_upi = sum(purch.filter(Account_Name__Account_Type='UPI').values_list('Paid_Amount', flat=True)) if purch.filter(Account_Name__Account_Type='UPI') != None else 0
		dp_bank = sum(purch.filter(Account_Name__Account_Type='Company').values_list('Paid_Amount', flat=True)) if purch.filter(Account_Name__Account_Type='Company') != None else 0
		dp_cash = sum(purch.filter(Account_Name__Account_Type='CASH').values_list('Paid_Amount', flat=True)) if purch.filter(Account_Name__Account_Type='CASH') != None else 0
	else:
		dp_upi, dp_bank, dp_cash = 0, 0, 0

	if exp:
		de_upi = sum(exp.filter(Account_Name__Account_Type='UPI').values_list('Issued_Amount', flat=True)) if exp.filter(Account_Name__Account_Type='UPI') != None else 0
		de_bank = sum(exp.filter(Account_Name__Account_Type='Company').values_list('Issued_Amount', flat=True)) if exp.filter(Account_Name__Account_Type='Company') != None else 0
		de_cash = sum(exp.filter(Account_Name__Account_Type='CASH').values_list('Issued_Amount', flat=True)) if exp.filter(Account_Name__Account_Type='CASH') != None else 0
	else:
		de_upi, de_bank, de_cash = 0, 0, 0

	d_upi, d_bank, d_cash = dp_upi+de_upi, dp_bank+de_bank, dp_cash+de_cash
	tcredits = {'c_bank':c_bank, 'c_upi':c_upi, 'c_cash':c_cash}
	tdebits = {'d_bank':d_bank, 'd_upi':d_upi, 'd_cash':d_cash}

	banks = Bank_Accounts.objects.filter(Status=1, RC__Short_Name=firm).order_by('Account_Type')
	bk, bk_cr, bk_db, t_bal = [], [], [], 0
	for x in banks:
		bk.append(x)
		if sales.filter(Account_Name=x):
			bk_cr.append(sum(sales.filter(Account_Name=x).values_list('Received_Amount', flat=True))) 
		else:
			bk_cr.append(0)

		pr1 = sum(purch.filter(Account_Name=x).values_list('Paid_Amount', flat=True)) if purch != None else 0
		ex1 = sum(exp.filter(Account_Name=x).values_list('Issued_Amount', flat=True)) if exp != None else 0
		bk_db.append((pr1+ex1))
		

		salest = sum(Payment_Status.objects.filter(Order_No__RC__Short_Name=firm, Account_Name=x).values_list('Received_Amount', flat=True))
		purcht = sum(Vendor_Payment_Status.objects.filter(PO_No__RC__Short_Name=firm,  Account_Name=x).values_list('Paid_Amount', flat=True))
		expt = sum(Debit_Amounts.objects.filter(RC__Short_Name=firm,  Account_Name=x).values_list('Issued_Amount', flat=True))

		x.Closing_Balance = int(x.Opening_Balance) + salest  - purcht - expt - int(x.Utilized_Balance)
		x.save()
		t_bal = t_bal + x.Closing_Balance
	
	data = zip(cat, receipt)
	data1 = zip(bk, bk_cr, bk_db)

	return render(request, 'projects/DailyFinance.html', {'pdata':pdata, 'firm':firm, 'data':data, 'data1':data1, 'tsales':tsales, 'tpurch':tpurch, 'texp':texp, 'dur':dur, 'sDate':sDate, 'eDate':eDate, 'tcredits':tcredits, 'tdebits':tdebits, 'banks':banks, 'fltbnk':fltbnk, 't_bal':t_bal})