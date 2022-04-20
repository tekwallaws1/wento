from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from .models import *
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


# Proposals Dashboard 
@login_required
def Prop_Dashboard(request):
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

	return render(request, 'proposals/ProposalsDB.html', {'d':d, 'x_30':x_30, 'y_30':y_30, 'x_90':x_90, 'y_90':y_90, 'x_180':x_180, 'y_180':y_180, 'x_365':x_365, 'y_365':y_365,} )

def Proposal_Form(request):
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
			print('kjkjk', fdata.Type)
			if fdata.Type == None:
				fdata.Type = 'Residential'

			# Generate Automatic Proposal Number and Date
			if last_proposal_no:
				last_proposal_no = last_proposal_no.Proposal_No_1
			else:
				last_proposal_no = 0
			fdata.Proposal_No_1 = int(last_proposal_no) + 1
			fy = get_financial_year(str(date.today()))
			fdata.Proposal_No = 'SSE/TS/'+str(fy)+'/'+str(fdata.Proposal_No_1)
			fdata.save()
			if request.user.username:
				return redirect('/proposalslist/')
			else:
				return render(request, 'proposals/ContactUs.html')		
		else:
			return HttpResponse('Data You Have Submitted is Not Valid/Sufficient, Please Go Back and Check and Submit Again')
	else:
		if request.user.username:
			form = ProposalForm()
			return render(request, 'proposals/ProposalForm1.html', {'form':form})
		else:
			form = Proposal1Form()
			return render(request, 'proposals/ProposalForm.html', {'form':form})

@login_required
def Proposals(request):
	table = Proposal.objects.all().order_by('Is_Gen').order_by('-id')
	filter_data = ProposalFilter(request.GET, queryset=table)
	table = filter_data.qs
	price = []
	user = []
	for x in table:
		try:
			qt = Quote.objects.get(Proposal_No_1=x.Proposal_No_1)
			fcost = int(qt.Tender_Cost+qt.Supplier_Add_On_Cost+qt.DD1_Charges+qt.DD2_Charges+qt.High_Raised_Structure-qt.Subsidy)
			usr = qt.Account
		except Quote.DoesNotExist:
			fcost = 'None' #Not yet generated
			usr = None
		price.append(fcost)
		user.append(usr)
		print(user)
	data = zip(table, price, user)
	return render(request, 'proposals/Proposals.html', {'data':data, 'filter_data':filter_data,})

@login_required
def Gen_Quote(request, fnc, var):
	user = Account.objects.get(User_Name=request.user.username)
	if not user:
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
			return HttpResponse('First Register Communication Company Address Under Specified State or Any State Based on Customer Request')

		# Get Costing Data Filter by Customer Requirement
		try:
			cost = Costing.objects.get(Capacity=pl.Capacity)
		except Costing.DoesNotExist:
			return HttpResponse('Costing Details For Customer Requested Model Capacity Has Not Been Generated')
		
		if pl.Type == 'Commercial':
			gst = int((cost.Tender_Cost+cost.Supplier_Add_On_Cost+cost.DD2_Charges+cost.High_Raised_Structure)*0.12)
			cost.DD1_Charges = 0
			cost.Subsidy = 0
		else:
			gst = 0

		fcost = int(cost.Tender_Cost+cost.Supplier_Add_On_Cost+cost.DD1_Charges+cost.DD2_Charges+cost.High_Raised_Structure+gst)
		
		qt = Quote.objects.create(Account=user, From_Company=cm, Proposal_To=pl, Proposal_No_1=pl.Proposal_No_1, Tender_Cost=cost.Tender_Cost, Supplier_Add_On_Cost=cost.Supplier_Add_On_Cost, DD1_Charges=cost.DD1_Charges, 
			DD2_Charges=cost.DD2_Charges, High_Raised_Structure=cost.High_Raised_Structure, Subsidy=cost.Subsidy, Cost_To_Client=fcost, Date=datetime.now(), GST_Amount=gst, Type=pl.Type, Rivision=1)
		# update proposal quote generation
		pl.Is_Gen = True
		pl.save()

		tcost = int(qt.Tender_Cost+qt.Supplier_Add_On_Cost+qt.DD1_Charges+qt.DD2_Charges+qt.High_Raised_Structure)
		fcost = int(tcost+gst-qt.Subsidy)
		word = num2words(fcost, to='cardinal', lang='en_IN')
		return render(request, 'proposals/Quote.html', {'qt':qt, 'word':word, 'tcost':tcost, 'fcost':fcost, 'gst':gst, 'user':user})
	elif fnc == 'delete':
		qt = Quote.objects.get(Proposal_No_1=var)
		qt.delete()
		prop = Proposal.objects.get(Proposal_No_1=var)
		prop.delete()
		messages.success(request, "Selected Proposal/Quote Details Has Been Deleted")
		return redirect('/proposalslist/')

	else:
		qt = Quote.objects.get(Proposal_No_1=var)
		print(user.Designation)
		if qt.Type == 'Commercial':
			gst = int((qt.Tender_Cost+qt.Supplier_Add_On_Cost+qt.DD1_Charges+qt.DD2_Charges+qt.High_Raised_Structure)*0.12)
		else:
			gst = 0
		tcost = int(qt.Tender_Cost+qt.Supplier_Add_On_Cost+qt.DD1_Charges+qt.DD2_Charges+qt.High_Raised_Structure)
		fcost = int(tcost+gst-qt.Subsidy)
		qt.Cost_To_Client = fcost
		qt.save()
		word = num2words(fcost, to='cardinal', lang='en_IN')
		return render(request, 'proposals/Quote.html', {'qt':qt, 'word':word, 'tcost':tcost, 'fcost':fcost, 'gst':gst, 'user':user})
			
@login_required
def Quote_Edit(request, var):
	data=get_object_or_404(Quote, Proposal_No_1=var)
	if request.method == 'POST':
		form = QuoteForm(request.POST, request.FILES, instance=data)
		if form.is_valid():
			p = form.save()
			fdata = Quote.objects.get(id=p.id)
			print(fdata)
			if fdata.Type == 'Commercial':
				gst = int((fdata.Tender_Cost+fdata.Supplier_Add_On_Cost++fdata.DD1_Charges+fdata.DD2_Charges+fdata.High_Raised_Structure)*0.12)
				fdata.Subsidy = 0
			else:
				gst = 0
			fdata.GST_Amount = gst
			clientcost = int(fdata.Tender_Cost+fdata.Supplier_Add_On_Cost++fdata.DD1_Charges+fdata.DD2_Charges+fdata.High_Raised_Structure+gst-fdata.Subsidy)
			fdata.Cost_To_Client = clientcost
			fdata.Date = datetime.now()
			fdata.save()

			form = QuoteForm()
			# messages.success(request, "Selected Quote Details Has Been Updated")
			return redirect('/quote/view/%s/'%var)
		else:
			return HttpResponse('Data You Have Submitted is Not Valid/Sufficient, Please Go Back and Check and Submit Again')
	else:
		form = QuoteForm(instance=data)
		return render(request, 'proposals/Quoteedit.html', {'form':form})

@login_required
def Prop_Edit(request, var):
	data=get_object_or_404(Proposal, Proposal_No_1=var)
	if request.method == 'POST':
		form = ProposalEditForm(request.POST, request.FILES, instance=data)
		if form.is_valid():
			p = form.save()
			pl = Proposal.objects.get(id=p.id)
			if pl.Type == None:
				pl.Type = 'Residential'
				pl.save()
			
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

				if pl.Type == 'Commercial':
					gst = int((cost.Tender_Cost+cost.Supplier_Add_On_Cost+cost.DD2_Charges+cost.High_Raised_Structure)*0.12)
					cost.Subsidy = 0
				else:
					gst = 0

				fcost = int(cost.Tender_Cost+cost.Supplier_Add_On_Cost+cost.DD1_Charges+cost.DD2_Charges+cost.High_Raised_Structure+gst+cost.Subsidy)
					
				updt = qt.update(From_Company=cm, Proposal_To=pl, Proposal_No_1=pl.Proposal_No_1, Tender_Cost=cost.Tender_Cost, Supplier_Add_On_Cost=cost.Supplier_Add_On_Cost, DD1_Charges=cost.DD1_Charges,
					DD2_Charges=cost.DD2_Charges, High_Raised_Structure=cost.High_Raised_Structure, Subsidy=cost.Subsidy, Date=datetime.now(), GST_Amount=gst, Cost_To_Client=fcost, Type=pl.Type, Rivision=1)
				# update proposal quote generation
			except Quote.DoesNotExist:
				pass

			messages.success(request, "Selected Proposal Details Has Been Updated")
			return redirect('/proposalslist/')
		else:
			return HttpResponse('Data You Have Submitted is Not Valid/Sufficient, Please Go Back and Check and Submit Again')
	else:
		form = ProposalEditForm(instance=data)
		return render(request, 'proposals/ProposalForm1.html', {'form':form})

#Copy proposal
@login_required
def Prop_Copy(request, var):
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
			return redirect('/proposalslist/')
		else:
			return HttpResponse('Data You Have Submitted is Not Valid/Sufficient, Please Go Back and Check and Submit Again')
	else:
		form = ProposalForm(instance=data)
		return render(request, 'proposals/ProposalForm1.html', {'form':form})

# For Customer Viewing Purpose Only
# @login_required
def Gen_Quote1(request, var, var1):
	qt = Quote.objects.filter(Proposal_No_1=var, Proposal_To__Phone_Number=var1).last()
	tcost = int(qt.Tender_Cost+qt.Supplier_Add_On_Cost+qt.DD1_Charges+qt.DD2_Charges+qt.High_Raised_Structure)
	fcost = int(tcost-qt.Subsidy+GST_Amount)
	word = num2words(fcost, to='cardinal', lang='en_IN')
	return render(request, 'proposals/Quote1.html', {'qt':qt, 'word':word, 'tcost':tcost, 'fcost':fcost})
	

@login_required
def Forms(request, fnc, var, rid):
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
				return redirect('/masterdatas/%s/'%var)
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
			return render(request, 'proposals/Forms.html', {'form': form, 'update':'true', 'var':var})

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
			data.ds = False
			data.save()
		messages.success(request, "Selected Details Has Been Sent to Recyclebin")
		return redirect('/masterdatas/%s/'%var)

	if request.method ==  'POST':
		if var == 'addcompany':
			form = CompanyDetailsForm(request.POST, request.FILES)
		elif var == 'addcapacity':
			form = PowerCatForm(request.POST, request.FILES)
		elif var == 'addcosting':
			form = CostingForm(request.POST, request.FILES)

		if form.is_valid():
			form.save()
			messages.success(request, "Data Has Been Added")
			return redirect('/masterdatas/%s/'%var)
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
			return render(request, 'proposals/Forms.html', {'form': form, 'var':var})
		else:
			if var == 'addcompany':
				form = CompanyDetailsForm()
			elif var == 'addcapacity':
				form = PowerCatForm()
			elif var == 'addcosting':
				form = CostingForm()
			return render(request, 'proposals/Forms.html', {'form': form, 'var':var})

@login_required
def Master_Data(request, var):
	if var == 'addcompany':
		table = CompanyDetails.objects.filter(ds=True).order_by('id')
	elif var == 'addcapacity':
		table = PowerCat.objects.filter(ds=True).order_by('id')
	elif var == 'addcosting':
		cost = Costing.objects.filter(ds=True).order_by('id')
		tcost = []
		fcost = []
		for x in cost:
			tc = int(x.Tender_Cost+x.Supplier_Add_On_Cost+x.DD1_Charges+x.DD2_Charges+x.High_Raised_Structure) or 0
			fc = int(tc-x.Subsidy) or 0
			tcost.append(tc)
			fcost.append(fc)
		table = zip(cost, tcost, fcost)
	return render(request, 'proposals/MasterData.html', {'table':table, 'var':var})






