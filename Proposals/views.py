from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from .models import *
from Orders.models import Orders
from Projects.models import *
from .forms import *
from .filters import *
from Projects.fyear import get_financial_year
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import date, datetime, timedelta 
import re
from django.db.models import Sum, Avg, Count
from itertools import chain
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Q
import random 
from django.urls import reverse   
import os
from django.conf import settings
from django.template.loader import get_template
from num2words import num2words
from Projects.basedata import projectname
 

# Proposals Dashboard 
@login_required
def Prop_Dashboard(request, proj):
	pdata = projectname(request, proj)
	qt = Quote.objects.all()
	qt_30d = Quote.objects.filter(Date__date__gte=date.today()-timedelta(days=30))
	prop_confirm = Quote.objects.filter(Status = 1)
	prop_confirm_30d = Quote.objects.filter(Date__date__gte=date.today()-timedelta(days=30), Status = 1)

	tprop = len(qt)
	tprop_30d = len(qt_30d)
	tprop_confirm = len(prop_confirm)
	tprop_confirm_30d = len(prop_confirm_30d)
	pend_tprop = tprop - tprop_confirm

	prop_val = 0
	prop_val_30d = 0
	confirm_val = 0
	confirm_30d = 0
 
	x_30  = []
	y_30  = []
	x_90  = []
	y_90  = []
	x_180 = []
	y_180 = []
	x_365 = []
	y_365 = []

	for x in qt:
		prop_val = int(prop_val + x.Cost_To_Client)
	for x in qt_30d:
		prop_val_30d = int(prop_val_30d + x.Cost_To_Client)
		x_30.append(str((x.Date+timedelta(days=1)).strftime('%m-%d-%Y')))
		y_30.append(x.Proposal_To.Capacity.Capacity)
	for x in prop_confirm:
		confirm_val = int(confirm_val + x.Cost_To_Client)
	for x in prop_confirm_30d:
		confirm_30d = int(confirm_30d + x.Cost_To_Client)

	qt90 = Quote.objects.filter(Date__date__gte=date.today()-timedelta(days=90))
	for x in qt90:
		x_90.append(str((x.Date+timedelta(days=1)).strftime('%m-%d-%Y')))
		y_90.append(x.Proposal_To.Capacity.Capacity)
	qt180 = Quote.objects.filter(Date__date__gte=date.today()-timedelta(days=180))
	for x in qt180:
		x_180.append(str((x.Date+timedelta(days=1)).strftime('%m-%d-%Y')))
		y_180.append(x.Proposal_To.Capacity.Capacity)
	qt365 = Quote.objects.filter(Date__date__gte=date.today()-timedelta(days=365))
	for x in qt365:
		x_365.append(str((x.Date+timedelta(days=1)).strftime('%m-%d-%Y')))
		y_365.append(x.Proposal_To.Capacity.Capacity)

	pend_prop_val = prop_val - confirm_val

	d = {'tprop':tprop, 'tprop_30d':tprop_30d, 'tprop_confirm':tprop_confirm, 'tprop_confirm_30d':tprop_confirm_30d, 
	'pend_tprop':pend_tprop, 'prop_val':prop_val, 'prop_val_30d':prop_val_30d, 'confirm_val':confirm_val, 'confirm_30d':confirm_30d, 'pend_prop_val':pend_prop_val}

	return render(request, 'proposals/ProposalsDB.html', {'d':d, 'x_30':x_30, 'y_30':y_30, 'x_90':x_90, 'y_90':y_90, 'x_180':x_180, 'y_180':y_180, 'x_365':x_365, 'y_365':y_365, 'pdata':pdata} )

# For marketing Open URL
def Proposal_Form1(request):
	last_proposal_no = Proposal.objects.all().last()
	if request.method == 'POST':
		if request.user.username:
			form = ProposalForm(request.POST)
		else:
			form = Proposal1Form(request.POST)
		if form.is_valid():
			p = form.save()
			fdata = Proposal.objects.get(id=p.id) 
			fdata.Date = datetime.now()
			if fdata.Capacity == None:
				if fdata.Power_Bill == 'Less than 1000':
					fdata.Capacity = PowerCat.objects.filter(Capacity=1).last()
				elif fdata.Power_Bill == '1000 to 3000':
					fdata.Capacity = PowerCat.objects.filter(Capacity=3).last()
				elif fdata.Power_Bill == '3000 to 6000':
					fdata.Capacity = PowerCat.objects.filter(Capacity=5).last()
				elif fdata.Power_Bill == 'Above 6000':
					fdata.Capacity = PowerCat.objects.filter(Capacity=10).last()
				else:
					fdata.Capacity = PowerCat.objects.filter(Capacity=3).last()
			else:
				pass

			# Generate Automatic Proposal Number and Date
			if last_proposal_no:
				last_proposal_no = last_proposal_no.Proposal_No_1
			else:
				last_proposal_no = 0
			fdata.Proposal_No_1 = int(last_proposal_no) + 1
			fy = get_financial_year(str(date.today()))
			fdata.Proposal_No = 'SSE/TS/'+str(fy)+'/'+str(fdata.Proposal_No_1)
			fdata.save()
			fdata1 = Proposal.objects.get(id=p.id)
			if fdata1.Inverter_Capacity == None:
				fdata1.Inverter_Capacity = fdata1.Capacity.Capacity
				fdata1.save()
			return render(request, 'proposals/ContactUs.html')		
		else:
			return HttpResponse('Data You Have Submitted is Not Valid/Sufficient, Please Go Back and Check and Submit Again')
	else:
		form = Proposal1Form()
		return render(request, 'proposals/ProposalForm.html', {'form':form})

@login_required
def Proposal_Form(request, proj):
	pdata = projectname(request, proj)
	last_proposal_no = Proposal.objects.all().last()
	if request.method == 'POST':
		if request.user.username:
			form = ProposalForm(request.POST)
		else:
			form = Proposal1Form(request.POST)
		if form.is_valid():
			p = form.save()
			fdata = Proposal.objects.get(id=p.id)
			fdata.Date = datetime.now()
			if fdata.Capacity == None:
				if fdata.Power_Bill == 'Less than 1000':
					fdata.Capacity = PowerCat.objects.filter(Capacity=1).last()
				elif fdata.Power_Bill == '1000 to 3000':
					fdata.Capacity = PowerCat.objects.filter(Capacity=3).last()
				elif fdata.Power_Bill == '3000 to 6000':
					fdata.Capacity = PowerCat.objects.filter(Capacity=5).last()
				elif fdata.Power_Bill == 'Above 6000':
					fdata.Capacity = PowerCat.objects.filter(Capacity=10).last()
				else:
					fdata.Capacity = PowerCat.objects.filter(Capacity=3).last()
			else:
				pass

			# Generate Automatic Proposal Number and Date
			if last_proposal_no:
				last_proposal_no = last_proposal_no.Proposal_No_1
			else:
				last_proposal_no = 0
			fdata.Proposal_No_1 = int(last_proposal_no) + 1
			fy = get_financial_year(str(date.today()))
			fdata.Proposal_No = 'SSE/TS/'+str(fy)+'/'+str(fdata.Proposal_No_1)
			fdata.save()
			fdata1 = Proposal.objects.get(id=p.id)
			if fdata1.Inverter_Capacity == None:
				fdata1.Inverter_Capacity = fdata1.Capacity.Capacity
				fdata1.save()

			if request.user.username:
				return redirect('/%s/proposalslist/'%pdata['pj'])
			else:
				return render(request, 'proposals/ContactUs.html')		
		else:
			return HttpResponse('Data You Have Submitted is Not Valid/Sufficient, Please Go Back and Check and Submit Again')
	else:
		if request.user.username:
			form = ProposalForm()
			return render(request, 'proposals/ProposalForm1.html', {'form':form, 'pdata':pdata})
		else:
			form = Proposal1Form()
			return render(request, 'proposals/ProposalForm.html', {'form':form, 'pdata':pdata})

@login_required
def Proposals(request, proj):
	pdata = projectname(request, proj)
	table = Proposal.objects.all().order_by('Is_Gen').order_by('-id')
	filter_data = ProposalFilter(request.GET, queryset=table)
	table = filter_data.qs
	price, user, is_order, pending, pc = [], [], [], 0, 0
	for x in table:
		try:
			qt = Quote.objects.get(Proposal_No_1=x.Proposal_No_1)
			if qt.Type != 'Residential':
				qt.Subsidy = 0
				cables = qt.Cables
			else:
				cables = 0
			fcost = int(qt.Tender_Cost+qt.Supplier_Add_On_Cost+qt.DD1_Charges+qt.DD2_Charges+qt.High_Raised_Structure-qt.Subsidy)
			if qt.Type != 'Residential':
				fcost = int(fcost + (fcost*0.12))
			usr = qt.Account

			if qt.Status == 1:
				is_order.append(1)
			else:
				is_order.append(0)
				pending = fcost + pending
				pc = pc+1

		except Quote.DoesNotExist:
			fcost = 'None' #Not yet generated
			usr = None
			is_order.append(0)
		price.append(fcost)
		user.append(usr)

	
	data = zip(table, price, user, is_order)
	return render(request, 'proposals/Proposals.html', {'data':data, 'filter_data':filter_data, 'pdata':pdata, 'pending':pending, 'pc':pc})

@login_required
def Proposal_To_Order(request, proj, var):
	pdata = projectname(request, proj)
	p = Quote.objects.get(Proposal_No_1=var)
	if p.Status != 1:
		# create customer details
		c_cust = CustDt.objects.create(Customer_Name=p.Proposal_To.Name, Short_Name=p.Proposal_To.Name[0:14], Address_Line_1=p.Proposal_To.Address_Line_1, Address_Line_2=p.Proposal_To.Address_Line_2, 
			State=p.Proposal_To.State, Phone_Number_1=p.Proposal_To.Phone_Number, Email=p.Proposal_To.Email, Related_Project=pdata['pj'])
		# create customer contact details
		c_custcont = CustContDt.objects.create(Customer_Name=c_cust, Contact_Person=c_cust.Customer_Name, 
			Phone_Number_1=c_cust.Phone_Number_1, Email=c_cust.Email)
		
		t1 = int(p.Tender_Cost+p.Supplier_Add_On_Cost+p.DD1_Charges+p.DD2_Charges+p.High_Raised_Structure)

		if p.Type != 'Residential':
			gst = (t1 + p.Cables)*0.12
		else:
			gst, p.Cables = 0, 0
		tf = t1 + gst + p.Cables
		
		create_order = Orders.objects.create(user=p.Account, Related_Project=pdata['pj'], Customer_Name=c_cust, Order_No=p.Proposal_To.Proposal_No, Order_Details=str(p.Proposal_To.Capacity), Order_Value=tf, 
			Order_Type='Confirmed', Order_Received_Date=datetime.now(), Order_Reference_Person=c_custcont, Order_Through='By Phone')
		messages.success(request, "Selected Proposal Has Been Converted as Order, Please Click on Edit Order If You Want To Edit Order Details")
		p.Status = 1
		p.save()
		return redirect('/%s/orderslist/Inprogress/'%pdata['pj'])
	else:
		messages.error(request, "Proposal already converted as order, if you wnat to modify/edit, go to orders and edit/modify.      Or Create duplicate proposal and convert as order")
		return redirect('/%s/proposalslist/'%pdata['pj'])


@login_required
def Gen_Quote(request, proj, fnc, var):
	pdata = projectname(request, proj)
	try:
		user = Account.objects.get(user=request.user)
	except Account.DoesNotExist:
		user = None
	if fnc == 'create':
		pl = Proposal.objects.get(id=var)
		if pl.State != None: #if customer gave state, then company address based on state
			cm = CompanyDetails.objects.filter(State='Telangana').last()
		else:
			cm = CompanyDetails.objects.filter(State='Telangana').last()
		# if no company address registered under state or not at all a single CompanyDetails
		if cm:
			pass
		else:
			messages.error(request, "First Register Communication Company Address Under Specified State or Any State Based on Customer Request")
			return redirect('/%s/proposalslist/'%pdata['pj'])
		# Get Costing Data Filter by Customer Requirement
		try:
			cost = Costing.objects.get(Capacity=pl.Capacity)
		except Costing.DoesNotExist:
			cost = Costing.objects.filter(Capacity=pl.Capacity.Capacity).last()
			if not cost:
				messages.error(request, "Costing Details For Customer Requested Model Capacity Has Not Been Generated, Go to costing and add costing details for the product")
				return redirect('/%s/proposalslist/'%pdata['pj'])
		
		if pl.Type == 'Commercial' or pl.Type == 'Industrial':
			gst = int((cost.Tender_Cost+cost.Supplier_Add_On_Cost+cost.DD1_Charges+cost.DD2_Charges+cost.High_Raised_Structure+cost.Cables)*0.12)
		else:
			gst = 0

		fcost = int(cost.Tender_Cost+cost.Supplier_Add_On_Cost+cost.DD1_Charges+cost.DD2_Charges)
		cl_cost = int(fcost-cost.Subsidy) #excluding structure and gst (if commercial excluding cables)
		
		qt = Quote.objects.create(Account=user, From_Company=cm, Proposal_To=pl, Proposal_No_1=pl.Proposal_No_1, Tender_Cost=cost.Tender_Cost, Supplier_Add_On_Cost=cost.Supplier_Add_On_Cost, DD1_Charges=cost.DD1_Charges, 
			DD2_Charges=cost.DD2_Charges, High_Raised_Structure=0, Subsidy=cost.Subsidy, Cost_To_Client=cl_cost, Date=datetime.now(), GST_Amount=gst, Type=pl.Type, Rivision=1)
		# update proposal quote generation
		pl.Is_Gen = True
		pl.save()

		tcost = int(qt.Tender_Cost+qt.Supplier_Add_On_Cost+qt.DD1_Charges+qt.DD2_Charges+qt.High_Raised_Structure+qt.Cables) #excluding subsidy and gst
		fcost = int(tcost+gst-qt.Subsidy) #final quote cost
		word = num2words(fcost, to='cardinal', lang='en_IN')
		return render(request, 'proposals/Quote.html', {'qt':qt, 'word':word, 'tcost':tcost, 'fcost':fcost, 'gst':gst, 'user':user, 'pdata':pdata})
	elif fnc == 'delete':
		try:
			qt = Quote.objects.get(Proposal_No_1=var)
			qt.delete()
		except Quote.DoesNotExist:
			pass
		prop = Proposal.objects.get(Proposal_No_1=var)
		prop.delete()
		messages.success(request, "Selected Proposal/Quote Details Has Been Deleted")
		return redirect('/%s/proposalslist/'%pdata['pj'])

	else:
		qt = Quote.objects.get(Proposal_No_1=var)
		if qt.Type != 'Residential':
			gst = int((qt.Tender_Cost+qt.Supplier_Add_On_Cost+qt.DD1_Charges+qt.DD2_Charges+qt.High_Raised_Structure+qt.Cables)*0.12)
		else:
			gst = 0
		tcost = int(qt.Tender_Cost+qt.Supplier_Add_On_Cost+qt.DD1_Charges+qt.DD2_Charges+qt.High_Raised_Structure+qt.Cables)
		fcost = int(tcost+gst-qt.Subsidy)

		cl_cost = fcost - gst - qt.High_Raised_Structure - qt.Cables

		if qt.Cost_To_Client != cl_cost:
			diff = qt.Cost_To_Client - cl_cost
			qt.Supplier_Add_On_Cost = qt.Supplier_Add_On_Cost + diff

		qt.save()
		word = num2words(fcost, to='cardinal', lang='en_IN')
		return render(request, 'proposals/Quote.html', {'qt':qt, 'word':word, 'tcost':tcost, 'fcost':fcost, 'gst':gst, 'user':user, 'pdata':pdata})
			
@login_required
def Quote_Edit(request, proj, var):
	pdata = projectname(request, proj)
	data=get_object_or_404(Quote, Proposal_No_1=var)
	if request.method == 'POST':
		form = QuoteForm(request.POST, request.FILES, instance=data)
		if form.is_valid():
			p = form.save()
			fdata = Quote.objects.get(id=p.id)
			if fdata.Type == 'Commercial' or fdata.Type == 'Industrial':
				gst = int((fdata.Tender_Cost+fdata.Supplier_Add_On_Cost+fdata.DD1_Charges+fdata.DD2_Charges+fdata.High_Raised_Structure+fdata.Cables)*0.12)
			else:
				gst = 0
			fdata.GST_Amount = gst
			cl_cost = int(fdata.Tender_Cost+fdata.Supplier_Add_On_Cost+fdata.DD1_Charges+fdata.DD2_Charges-fdata.Subsidy)

			if fdata.Cost_To_Client != cl_cost:
				diff = fdata.Cost_To_Client - cl_cost
				fdata.Supplier_Add_On_Cost = fdata.Supplier_Add_On_Cost + diff

			fdata.Date = datetime.now()
			l = fdata.save()
			print(l)

			form = QuoteForm()
			# messages.success(request, "Selected Quote Details Has Been Updated")
			url = '/' + str(pdata['pj']) + '/quote/view/' + var + '/'
			# return HttpResponse(url)
			return redirect(url)
		else:
			messages.error(request, "Data You Have Submitted is Not Valid/Sufficient, Please Go Back and Check and Submit Again")
			return redirect('/%s/proposalslist/'%pdata['pj'])
	else:
		form = QuoteForm(instance=data)
		return render(request, 'proposals/Quoteedit.html', {'form':form, 'pdata':pdata})

@login_required
def Prop_Edit(request, proj, var):
	pdata = projectname(request, proj)
	data=get_object_or_404(Proposal, Proposal_No_1=var)
	if request.method == 'POST':
		form = ProposalEditForm(request.POST, request.FILES, instance=data)
		if form.is_valid():
			p = form.save()
			pl = Proposal.objects.get(id=p.id)			
			try:
				qt = Quote.objects.filter(Proposal_No_1=pl.Proposal_No_1)
				if pl.State != None: #if customer gave state, then company address based on state
					cm = CompanyDetails.objects.filter(State='Telangana').last()
				else:
					cm = CompanyDetails.objects.filter(State='Telangana').last()
				# if no company address registered under state or not at all a single CompanyDetails
				if cm:
					pass
				else:
					return HttpResponse('First Register Communication Company Address Under Specified State or Any State Based on Customer Request')

				# Get Costing Data Filter by Customer Requirement
				try:
					cost = Costing.objects.get(Capacity=pl.Capacity)
				except Costing.DoesNotExist:
					return HttpResponse('Costing Details For Customer Requested Model Capacity Has Not Been Generated')

				if pl.Type == 'Commercial' or pl.Type == 'Industrial':
					gst = int((cost.Tender_Cost+cost.Supplier_Add_On_Cost+cost.DD2_Charges+cost.High_Raised_Structure+cost.Cables)*0.12)
					cost.Subsidy = 0
				else:
					gst = 0

				fcost = int(cost.Tender_Cost+cost.Supplier_Add_On_Cost+cost.DD1_Charges+cost.DD2_Charges+cost.High_Raised_Structure+gst+cost.Subsidy+cost.Cables)
					
				updt = qt.update(From_Company=cm, Proposal_To=pl, Proposal_No_1=pl.Proposal_No_1, Tender_Cost=cost.Tender_Cost, Supplier_Add_On_Cost=cost.Supplier_Add_On_Cost, DD1_Charges=cost.DD1_Charges,
					DD2_Charges=cost.DD2_Charges, High_Raised_Structure=cost.High_Raised_Structure, Subsidy=cost.Subsidy, Date=datetime.now(), GST_Amount=gst, Cost_To_Client=fcost, Type=pl.Type, Rivision=1)
				# update proposal quote generation
			except Quote.DoesNotExist:
				pass

			messages.success(request, "Selected Proposal Details Has Been Updated")
			return redirect('/%s/proposalslist/'%pdata['pj'])
		else:
			return HttpResponse('Data You Have Submitted is Not Valid/Sufficient, Please Go Back and Check and Submit Again')
	else:
		form = ProposalEditForm(instance=data)
		return render(request, 'proposals/ProposalForm1.html', {'form':form, 'pdata':pdata})

#Copy proposal
@login_required
def Prop_Copy(request, proj, var):
	pdata = projectname(request, proj)
	last_proposal_no = Proposal.objects.all().last()
	data=get_object_or_404(Proposal, Proposal_No_1=var)
	if request.method == 'POST':
		form = ProposalForm(request.POST)
		if form.is_valid():
			p = form.save()
			fdata = Proposal.objects.get(id=p.id)
			fdata.Date = datetime.now()
			if fdata.Type == None:
				fdata.Type == 'Residential'
			# Generate Automatic Proposal Number and Date
			if last_proposal_no:
				last_proposal_no = last_proposal_no.Proposal_No_1
			else:
				last_proposal_no = 0
			fdata.Proposal_No_1 = int(last_proposal_no) + 1
			fdata.Proposal_No = 'SSE/TS/22-23/'+str(fdata.Proposal_No_1)
			fdata.save()
			messages.success(request, "Proposal Has Been Created")
			return redirect('/%s/proposalslist/'%pdata['pj'])
		else:
			return HttpResponse('Data You Have Submitted is Not Valid/Sufficient, Please Go Back and Check and Submit Again')
	else:
		form = ProposalForm(instance=data)
		return render(request, 'proposals/ProposalForm1.html', {'form':form, 'pdata':pdata})

# For Customer Viewing Purpose Only
# @login_required
def Gen_Quote1(request, var, var1):
	pl = Proposal.objects.get(Proposal_No_1=var)
	qt = Quote.objects.filter(Proposal_No_1=var, Proposal_To__Phone_Number=var1).last()
	if qt.Type != 'Residential':
		gst = int((qt.Tender_Cost+qt.Supplier_Add_On_Cost+qt.DD1_Charges+qt.DD2_Charges+qt.High_Raised_Structure+qt.Cables)*0.12)
	else:
		gst = 0
	tcost = int(qt.Tender_Cost+qt.Supplier_Add_On_Cost+qt.DD1_Charges+qt.DD2_Charges+qt.High_Raised_Structure+qt.Cables)
	fcost = int(tcost+gst-qt.Subsidy)
	word = num2words(fcost, to='cardinal', lang='en_IN')
	return render(request, 'proposals/Quote1.html', {'qt':qt, 'word':word, 'tcost':tcost, 'fcost':fcost, 'gst':gst})
	

@login_required
def Forms(request, proj, fnc, var, rid):
	pdata = projectname(request, proj)
	if fnc != 'create' and fnc != 'delete' and fnc!='copy' : #for update checking
		if request.method ==  'POST':
			if var == 'addcompany':
				data=get_object_or_404(CompanyDetails, id=rid)
				form = CompanyDetailsForm(request.POST, request.FILES, instance=data)
			elif var == 'addcapacity':
				data=get_object_or_404(PowerCat, id=rid)
				form = PowerCatForm(request.POST, request.FILES, instance=data)
			elif var == 'addcosting':
				data=get_object_or_404(Costing, id=rid)
				form = CostingForm(request.POST, request.FILES, instance=data)

			if form.is_valid():
				form.save()
				messages.success(request, "Selected Details Has Been Updated")
				url = '/' + str(pdata['pj']) + '/masterdatas/' + var + '/'
				return redirect(url)
			else:
				return HttpResponse('Please Enter Valid Data, Go Back and Check, Because You Might Be Already Generated Same Data or You Might Enter Wrong Data')
		else:
			if var == 'addcompany':
				data=get_object_or_404(CompanyDetails, id=rid)
				form = CompanyDetailsForm(instance=data)
			elif var == 'addcapacity':
				data=get_object_or_404(PowerCat, id=rid)
				form = PowerCatForm(instance=data)
			elif var == 'addcosting':
				data=get_object_or_404(Costing, id=rid)
				form = CostingForm(instance=data)
			return render(request, 'proposals/Forms.html', {'form': form, 'update':'true', 'var':var, 'pdata':pdata})

	elif fnc == 'delete':
		if var == 'addcompany':
			data=get_object_or_404(CompanyDetails, id=rid)
			data.ds = False
			data.save()
		elif var == 'addcapacity':
			data=get_object_or_404(PowerCat, id=rid)
			data.ds = False
			data.save()
		elif var == 'addcosting':
			data=get_object_or_404(Costing, id=rid)
			data.delete() #if any field unique you can delete instaed of ds=0 hide
		messages.success(request, "Selected Details Has Been Sent to Recyclebin")
		url = '/' + str(pdata['pj']) + '/masterdatas/' + var + '/'
		return redirect(url)

	if request.method ==  'POST':
		if var == 'addcompany':
			form = CompanyDetailsForm(request.POST, request.FILES)
		elif var == 'addcapacity':
			form = PowerCatForm(request.POST, request.FILES)
		elif var == 'addcosting':
			form = CostingForm(request.POST, request.FILES)

		if form.is_valid():
			p = form.save()
			if var == 'addcapacity':
				ref1 = PowerCat.objects.get(id=p.id)
				cap_count = len(PowerCat.objects.filter(Capacity=ref1.Capacity, ds=1))
				new_ref_no = cap_count
				if cap_count>9:
					ref_no = str(ref1.Capacity)+'KW'+str(new_ref_no)
				else:
					ref_no = str(ref1.Capacity)+'KW0'+str(new_ref_no)
				ref1.Ref_No = ref_no
				ref1.save()
			messages.success(request, "Data Has Been Added")
			url = '/' + str(pdata['pj']) + '/masterdatas/' + var + '/'
			return redirect(url)
		else:
			return HttpResponse('Please Enter Valid Data, Go Back and Check, Because You Might Be Already Generated Same Data or You Might Enter Wrong Data')
	else:
		if fnc == 'copy':
			if var == 'addcompany':
				data=get_object_or_404(CompanyDetails, id=rid)
				form = CompanyDetailsForm(instance=data)
			elif var == 'addcapacity':
				data=get_object_or_404(PowerCat, id=rid)
				form = PowerCatForm(instance=data)
			elif var == 'addcosting':
				data=get_object_or_404(Costing, id=rid)
				form = CostingForm(instance=data)
			else:
				return HttpResponse('Please Enter Valid Data, Go Back and Check, Because You Might Be Already Generated Same Data or You Might Enter Wrong Data')
			return render(request, 'proposals/Forms.html', {'form': form, 'var':var, 'pdata':pdata})
		else:
			if var == 'addcompany':
				form = CompanyDetailsForm()
			elif var == 'addcapacity':
				form = PowerCatForm()
			elif var == 'addcosting':
				form = CostingForm()
			return render(request, 'proposals/Forms.html', {'form': form, 'var':var, 'pdata':pdata})

@login_required
def Master_Data(request, proj, var):
	pdata = projectname(request, proj)
	if var == 'addcompany':
		table = CompanyDetails.objects.filter(ds=True).order_by('id')
	elif var == 'addcapacity':
		table = PowerCat.objects.filter(ds=True).order_by('id')
	elif var == 'addcosting':
		cost = Costing.objects.filter(ds=True).order_by('id')
		tcost = []
		fcost = []
		for x in cost:
			tc = int(x.Tender_Cost+x.Supplier_Add_On_Cost+x.DD1_Charges+x.DD2_Charges+x.Cables) or 0
			fc = int(tc-x.Subsidy) or 0
			tcost.append(tc)
			fcost.append(fc)
		table = zip(cost, tcost, fcost)
	return render(request, 'proposals/MasterData.html', {'table':table, 'var':var, 'pdata':pdata})




