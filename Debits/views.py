from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from datetime import date, datetime, timedelta
# from dateutil.relativedelta import relativedelta 
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Projects.fyear import get_financial_year, get_fy_date, get_fy_date_fy
from Projects.basedata import projectname
from json import dumps
from .forms import *
from .filters import *
from num2words import num2words
from django.db.models import Q
import calendar
from calendar import monthrange



def get_errors(request, formerrors): 
	x = 'Errors: '
	for field, errors in formerrors.items():
			x = x + ('{}'.format(','.join(errors))) + ' '
	return x

def update_expense_items(request, expid, itemid):
	exp = Expenses.objects.get(id=expid)
	if itemid != None:
		item = Exp_Items.objects.get(id=itemid)
		item.Expenses = exp
		item.save()
		exp.Total_Amount = sum(Exp_Items.objects.filter(Expenses=exp).values_list('Amount', flat=True)) or 0
		due = Expenses.objects.filter(Submitted_By=exp.Submitted_By, Lock_Status=1).order_by('-id')
		due = due[1].Balance_Amount if len(due) > 1 else 0
		exp.Balance_Amount = exp.Total_Amount + due
		exp.save()

		dates = []
		for x in Exp_Items.objects.filter(Expenses=exp):
			dates.append(x.From_Date)
			if x.To_Date:
				dates.append(x.To_Date)
		dates = list(dict.fromkeys(dates))
		dt_max = max(dates, key= lambda d: datetime.strptime(str(d), '%Y-%m-%d'))
		dt_min = min(dates, key= lambda d: datetime.strptime(str(d), '%Y-%m-%d'))
		if dt_max == dt_min:
			exp.From_Date = dt_min
			exp.save()
		else:
			exp.From_Date = dt_min
			exp.To_Date = dt_max
			exp.save()
	else:
		exp.Total_Amount, exp.Balance_Amount = None, None
		exp.save()

def get_expenses_ref_no(request, expid):
	fd = Expenses.objects.get(id=expid)
	fd.FY = get_financial_year(str(date.today()))

	if len(Expenses.objects.all()) > 1:
		last_expid =  Expenses.objects.all().order_by('-id')[1]
	else:
		last_expid = None

	last_expno = Expenses.objects.get(id=last_expid.id) if last_expid != None else None

	if last_expno != None:		
		if fd.FY == last_expno.FY:
			fd.Ref_No = last_expno.Ref_No + 1
		else:
			fd.Ref_No = 1
	else:
		fd.Ref_No = 1 
	
	if len(str(fd.Ref_No)) == 1: 
		expno1 = '00'+str(fd.Ref_No)
	elif len(str(fd.Ref_No)) == 2:
		expno1 = '0'+str(fd.Ref_No)
	else:
		expno1 = fd.Ref_No	

	fd.Reference_No = 'ER'+str(fd.FY)+'/'+str(expno1)
	fd.save()

def get_debitvoucher_num(request, df):
	if df != None:
		n = df.Voucher_No + 1
	else:
		n = 1
	return n


def update_exp_duedays(request, expid):
	exp = Expenses.objects.get(id=expid)
	exp.Over_Due_Days = (date.today() - exp.Submitted_Date).days
	if exp.Over_Due_Days < 0:
		exp.Over_Due_Days = 0
	exp.save()

def exp_update(request, expid):
	exp = Expenses.objects.get(id=expid)
	exp.Balance_Amount = exp.Total_Amount
	exp.save()
	# empl_adv = Staff_Advances.objects.filter(Employ=exp.Submitted_By).last()
	# adv = empl_adv.Advance if empl_adv else None
	# if adv != None:
	# 	if adv != 0:
	# 		exp.Balance_Advance = adv
	# 		exp.save()
	# 		if adv >= exp.Total_Amount:
	# 			exp.Balance_Amount = 0
	# 			exp.save()
	# 		else:
	# 			exp.Balance_Amount = exp.Total_Amount - adv
	# 			exp.save()
	# else:
	# 	exp.Balance_Amount = exp.Total_Amount
	# 	exp.save()


def exp_apr_update(request, expid):
	exp = Expenses.objects.filter(id=expid).update(Approval_Status=1)
	exp = Expenses.objects.get(id=expid)
	empl_adv = Staff_Advances.objects.filter(Employ=exp.Submitted_By).last()
	adv = empl_adv.Advance if empl_adv else None
	dbt = Debit_Amounts.objects.filter(Employ=exp.Submitted_By)
	if adv != None:
		if dbt:
			if adv != 0:
				if adv >= exp.Total_Amount:
					exp.Balance_Amount = 0
					exp.Issued_Date = empl_adv.Issued_Date
					exp.Clearing_Status = 1
					exp.Issued_By = empl_adv.Issued_By
					exp.save()
					empl_adv.Advance = adv - exp.Total_Amount
					empl_adv.save()
				else:
					exp.Balance_Amount = exp.Total_Amount - adv
					exp.Issued_Date = empl_adv.Issued_Date
					exp.Issued_By = empl_adv.Issued_By
					exp.save()
					empl_adv.Advance = 0
					empl_adv.save()
			else:
				exp.Balance_Amount = exp.Total_Amount
				exp.save()
		else:
			empl_adv.delete()
			exp.Balance_Amount = exp.Total_Amount
			exp.save()
	else:
		exp.Balance_Amount = exp.Total_Amount
		exp.save()


def update_debits(request, did, fnc):
	df = Debit_Amounts.objects.get(id=did)
	if df.Party_Name:
		df.Issued_To = None
		df.Expenses = None
		if not df.Amount_to_be_Pay:
			df.Amount_to_be_Pay = df.Issued_Amount
		df.save()
	elif df.Expenses:
		df.Issued_To = None
		df.Party_Name = None
		df.save()
	else:
		df.Expenses = None
		df.Party_Name = None
		df.save()
	if df.Expenses or df.Issued_To:
		if df.Expenses:
			df.Employ = df.Expenses.Submitted_By
		else:
			df.Employ = df.Issued_To
		df.save()
		# employ = df.Employ
	
	df = Debit_Amounts.objects.get(id=did)
	# direct debits to invoice clearance if debit against invoice
	if df.Expenses:
		if fnc == 'create':
			exp = Expenses.objects.filter(id=df.Expenses.id)
			diff = add_exp(request, exp, df.Issued_Amount, df) # against that particular expenses
			if df.Employ:
				if diff == 0:
					return 1
				if diff > 0:
					exp = Expenses.objects.filter(Submitted_By=df.Employ, Balance_Amount__gt=0, Approval_Status=1).order_by('Submitted_By') 
					diff = add_exp(request, exp, diff, df)
					if diff > 0:
						add_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), diff, df)				
		else:
			exp = Expenses.objects.filter(id=df.Expenses.id).last()
			if df.Issued_Amount >= exp.Total_Amount:
				exp.Balance_Amount, exp.Issued_By, exp.Issued_Date, exp.Clearing_Status = 0, df.Issued_By, df.Issued_Date, 1
				exp.save() 
			diff = add_exp(request, Expenses.objects.filter(id=df.Expenses.id), df.Issued_Amount, df)
			edit_dbt(request, exp, df)			
	else:
		if df.Paid_To == 'As Advance to Staff':
			if df.Related_To != 'Salary Advance':
				if fnc == 'create':
					exp = Expenses.objects.filter(Submitted_By=df.Employ, Balance_Amount__gt=0, Approval_Status=1).order_by('Submitted_By')
					diff = add_exp(request, exp, df.Issued_Amount, df)
					if diff > 0:
						add_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), diff, df)
				else:
					t_exps = sum(Expenses.objects.filter(Submitted_By=df.Employ, Approval_Status=1).values_list('Total_Amount', flat=True)) or 0
					t_dbts = sum(Debit_Amounts.objects.filter(Employ=df.Employ).exclude(Related_To='Salary Advance').values_list('Issued_Amount', flat=True)) or 0
					if t_dbts >= t_exps:
						Expenses.objects.filter(Submitted_By=df.Employ, Balance_Amount__gt=0).update(Balance_Amount=0, Issued_Date = df.Issued_Date, Issued_By = df.Issued_By, Clearing_Status = 1)
						diff = t_dbts - t_exps
						if diff == 0:
							updt_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), diff, df)
							return 1
						if diff > 0:
							updt_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), diff, df)
							return 1
					else:
						t_exps_bal = sum(Expenses.objects.filter(Submitted_By=df.Employ, Approval_Status=1).values_list('Balance_Amount', flat=True)) or 0
						t_exps_issue = t_exps - t_exps_bal
						if t_dbts < t_exps_issue: # it should equal otherwise we need to deduct somewhere
							updt_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), 0, df)
							set_expns = Expenses.objects.filter(Submitted_By=df.Employ, Balance_Amount__gt=0, Approval_Status=1).order_by('-Submitted_By')
							diff = t_exps_issue - t_dbts
							diff = del_exp(request, set_expns, diff)
							if diff > 0:
								set_expns = Expenses.objects.filter(Submitted_By=df.Employ, Balance_Amount=0, Approval_Status=1).order_by('-Submitted_By')
								diff = del_exp(request, set_expns, diff)
								if diff > 0:
									diff = del_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), diff)	
									return 1
						elif t_dbts > t_exps_issue:
							diff = t_dbts - t_exps_issue 
							set_expns = Expenses.objects.filter(Submitted_By=df.Employ, Balance_Amount__gt=0, Approval_Status=1).order_by('Submitted_By')
							diff = add_exp(request, set_expns, diff, df)
							if diff > 0:
								updt_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), diff, df)
						else:
							updt_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), 0, df)



    # test cases
	# against expenses
	# create: case11:first need to add/clear against that expnses
	# 	   case2: if still more balance after clear againt that particular invoice add to expenses which are 
	# 	   having due more than 0 submitted date wise
	# 	   case3: if still balance after all adding -> add balance to advance to related staff
	# edit: case1: if amount is leass that that against expenses direct adjustment against that expenses
	# 	  case2: if amount is more than expenses, 
	# 	  step1: first clear that expense
	# 	  step2: check all debits and expenses against that staff
	# 	  step3: if all all debits is more than all expenses, 
	# 	         -> clear all expenses, if any still balance add to advances
	# 	  step4: else if all debits is less than all expenses, may we need to deduct amount from expenses or not, for that
	# 	  		-> check all issued amounts against expenses (total - balance)
	# 	  		-> if isuued is less than all debit amount, we need to deduct amounts from Expenses
	# 	  		-> exclude that particular expense
	# 	  		-> filter due more than 0 date wise and deduct
	# 	  		-> if still need to deduct, filter cleared expenses and deduct datewise
	#           -> if still need to deduct, deduct from advances 

	# against staff as advance
	# create/edit: get all expenses to that staff, get all beit amount against that staff, adjust duewise by dtewise
	#              if still balance add to advance against that staff

def edit_dbt(request, exp, df):
	if df.Employ:
		t_exps = sum(Expenses.objects.filter(Submitted_By=df.Employ, Approval_Status=1).values_list('Total_Amount', flat=True)) or 0
		t_dbts = sum(Debit_Amounts.objects.filter(Employ=df.Employ).exclude(Related_To='Salary Advance').values_list('Issued_Amount', flat=True)) or 0
		if t_dbts >= t_exps:
			Expenses.objects.filter(Submitted_By=df.Employ, Balance_Amount__gt=0).update(Balance_Amount=0, Issued_Date = df.Issued_Date, Issued_By = df.Issued_By, Clearing_Status = 1)
			diff = t_dbts - t_exps
			if diff == 0:
				updt_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), diff, df)
				return 1
			if diff > 0:
				updt_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), diff, df)
		else:
			t_exps_bal = sum(Expenses.objects.filter(Submitted_By=df.Employ, Approval_Status=1).values_list('Balance_Amount', flat=True)) or 0
			t_exps_issue = t_exps - t_exps_bal
			if t_dbts < t_exps_issue: # it should equal otherwise we need to deduct somewhere
				updt_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), 0, df)
				set_expns = Expenses.objects.filter(Submitted_By=df.Employ, Balance_Amount__gt=0, Approval_Status=1).order_by('Submitted_By').exclude(Reference_No=exp.Reference_No)
				diff = t_exps_issue - t_dbts
				diff = del_exp(request, set_expns, diff)
				if diff > 0:
					set_expns = Expenses.objects.filter(Submitted_By=df.Employ, Balance_Amount=0, Approval_Status=1).order_by('Submitted_By').exclude(Reference_No=exp.Reference_No)
					diff = del_exp(request, set_expns, diff)
					if diff > 0:
						set_expns = Expenses.objects.filter(Reference_No=exp.Reference_No)
						diff = del_exp(request, set_expns, diff)
						# if diff > 0:
						# diff = del_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), diff, df)
			elif t_dbts > t_exps_issue:
				diff = t_dbts - t_exps_issue 
				set_expns = Expenses.objects.filter(Submitted_By=df.Employ, Balance_Amount__gt=0, Approval_Status=1).order_by('Submitted_By').exclude(Reference_No=exp.Reference_No)
				diff = add_exp(request, set_expns, diff, df)
				if diff > 0:
					set_expns = Expenses.objects.filter(Reference_No=exp.Reference_No)
					diff = add_exp(request, set_expns, diff, df)
					if diff > 0:
						updt_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), diff, df)
			else:
				updt_adv(request, Staff_Advances.objects.filter(Employ=df.Employ).last(), 0, df)

def edit_dbt1(request, employ):
	t_exps = sum(Expenses.objects.filter(Submitted_By=employ, Approval_Status=1).values_list('Total_Amount', flat=True)) or 0
	t_dbts = sum(Debit_Amounts.objects.filter(Employ=employ).exclude(Related_To='Salary Advance').values_list('Issued_Amount', flat=True)) or 0			
	t_exps_bal = sum(Expenses.objects.filter(Submitted_By=employ, Approval_Status=1).values_list('Balance_Amount', flat=True)) or 0
	t_exps_issue = t_exps - t_exps_bal
	if t_dbts < t_exps_issue: # it should equal otherwise we need to deduct somewhere
		updt_adv(request, Staff_Advances.objects.filter(Employ=employ).last(), 0, None)
		set_expns = Expenses.objects.filter(Submitted_By=employ, Balance_Amount__gt=0, Approval_Status=1).order_by('-Submitted_By')
		diff = t_exps_issue - t_dbts
		diff = del_exp(request, set_expns, diff)
		if diff > 0:
			set_expns = Expenses.objects.filter(Submitted_By=employ, Balance_Amount=0, Approval_Status=1).order_by('-Submitted_By')
			diff = del_exp(request, set_expns, diff)
			if diff > 0:
				diff = del_adv(request, Staff_Advances.objects.filter(Employ=employ).last(), diff)	
				return 1
	elif t_dbts > t_exps_issue:
		diff = t_dbts - t_exps_issue 
		set_expns = Expenses.objects.filter(Submitted_By=employ, Balance_Amount__gt=0, Approval_Status=1).order_by('Submitted_By')
		diff = add_exp(request, set_expns, diff, None)
		if diff > 0:
			updt_adv(request, Staff_Advances.objects.filter(Employ=employ).last(), diff, None)
	else:
		updt_adv(request, Staff_Advances.objects.filter(Employ=employ).last(), 0, None)


def delete_debit(request, amount, expid, empl):
	if expid:
		exp = Expenses.objects.filter(id=expid).last()
		if exp.Total_Amount <= amount:
			diff = amount - exp.Total_Amount + exp.Balance_Amount
			Expenses.objects.filter(id=expid).update(Balance_Amount=exp.Total_Amount, Clearing_Status=0, Issued_By=None, Issued_Date=None)
		else:
			diff = del_exp(request, Expenses.objects.filter(id=expid), amount)
		edit_dbt1(request, empl)
		# if diff > 0:
		# 	diff = del_adv(request, Staff_Advances.objects.filter(Employ=empl).last(), diff)
		# 	if diff > 0:
		# 		set_expns = Expenses.objects.filter(Submitted_By=empl, Balance_Amount__gt=0, Approval_Status=1).order_by('-Submitted_By')
		# 		diff = del_exp(request, set_expns, diff)
		# 		if diff > 0:
		# 			set_expns = Expenses.objects.filter(Submitted_By=empl, Balance_Amount=0, Approval_Status=1).order_by('-Submitted_By')
		# 			diff = del_exp(request, set_expns, diff)
	else:
		if empl:
			diff = del_adv(request, Staff_Advances.objects.filter(Employ=empl).last(), amount)
			if diff > 0:
				set_expns = Expenses.objects.filter(Submitted_By=empl, Balance_Amount__gt=0, Approval_Status=1).order_by('-Submitted_By')
				diff = del_exp(request, set_expns, diff)
				if diff > 0:
					set_expns = Expenses.objects.filter(Submitted_By=empl, Balance_Amount=0, Approval_Status=1).order_by('-Submitted_By')
					diff = del_exp(request, set_expns, diff)

def add_exp(request, exp, diff, df):
	for x in exp:
		if diff >= x.Balance_Amount:
			diff = 	diff - 	x.Balance_Amount
			x.Balance_Amount = 0
			if df != None:
				x.Issued_By = df.Issued_By
				x.Issued_Date = df.Issued_Date
			x.Clearing_Status = 1
			x.save()				
		else:
			x.Balance_Amount = x.Balance_Amount - diff
			if df != None:
				x.Issued_Date = df.Issued_Date
				x.Issued_By = df.Issued_By
			x.Clearing_Status = 0
			x.save()
			diff = 0
	
	return diff

def del_exp(request, exp, diff):
	for x in exp:
		if diff >= (x.Total_Amount - x.Balance_Amount):
			diff = 	diff - x.Total_Amount + x.Balance_Amount
			x.Balance_Amount = x.Total_Amount
			x.Issued_Date = None
			x.Clearing_Status = 0
			x.Issued_By = None
			x.save()				 					
		else:
			x.Balance_Amount = x.Balance_Amount + diff
			x.Clearing_Status = 0
			x.save()
			diff = 0

	return diff


def add_adv(request, empl, adv, df):
	if empl:
		ad = empl.Advance + adv if empl.Advance != None else adv
		empl.Advance = ad
		if df != None:
			empl.Issued_By, empl.Issued_Date = df.Issued_By, df.Issued_Date
		empl.save()
	else:
		Staff_Advances.objects.create(Employ=df.Employ, Advance=adv, Issued_By=df.Issued_By, Issued_Date=df.Issued_Date)
	return 1

def updt_adv(request, empl, adv, df):
	if empl:
		empl.Advance = adv
		if df != None:
			empl.Issued_By, empl.Issued_Date = df.Issued_By, df.Issued_Date
		empl.save()
	else:
		Staff_Advances.objects.create(Employ=df.Employ, Advance=adv, Issued_By=df.Issued_By, Issued_Date=df.Issued_Date)
	return 1

def del_adv(request, empl, adv):
	if empl:
		ad = empl.Advance - adv if empl.Advance != None else 0
		diff = adv - empl.Advance
		if ad < 0:
			ad = 0
		empl.Advance = ad
		empl.save()
		if diff <= 0:
			diff = 0
		return diff		
	else:
		return adv



def working_days(request, dt):
	# CASE1 - call when monthly attendance open
	# CASE2 - call only when attendance available belongs to that month	
	sDate = date(dt.year, dt.month, 1)
	lastdate = calendar.monthrange(dt.year, dt.month)[1]
	if dt.month == date.today().month:
		eDate = dt
	else: 
		eDate = date(dt.year,  dt.month, lastdate)

	sundays = len([1 for i in calendar.monthcalendar(sDate.year, sDate.month) if i[6] != 0 and eDate.day>=i[6]])
	fullday_holidays = len(DeclareDayAs.objects.filter(Date__gte=sDate).filter(Date__lte=eDate, Declare_Day_As='Holiday')) or 0
	halfday_holidays = len(DeclareDayAs.objects.filter(Date__gte=sDate).filter(Date__lte=eDate, Declare_Day_As='Half Day')) or 0
	force_work_days = len(DeclareDayAs.objects.filter(Date__gte=sDate).filter(Date__lte=eDate, Declare_Day_As='Working Day')) or 0
	total_working_days = int(eDate.day) + force_work_days - sundays - fullday_holidays - (halfday_holidays/2)
	workdays = Working_Days.objects.filter(Month__month=eDate.month, Month__year=eDate.year).last()
	if workdays:
		workdays.Working_Days = total_working_days
		workdays.save()
	else:
		workdays = Working_Days.objects.create(Working_Days=total_working_days, Month=eDate)
	return total_working_days

def update_month_atnd(request, pid):
	p = Attendance.objects.get(id=pid)
	if p.Start_Time != None and p.End_Time != None:
		sTime = datetime.strptime(str(p.Start_Time), "%H:%M:%S")
		eTime = datetime.strptime(str(p.End_Time), "%H:%M:%S")
		t_hours = (eTime-sTime).seconds/3600 #in hours
		p.Total_Hours = t_hours
		p.save()

	month = p.Date.month
	yr = p.Date.year

	atnd = Attendance.objects.filter(Date__month=month, Date__year=p.Date.year, Name=p.Name).order_by('Date')
	presents = len(atnd.filter(Day_Status = 'Present')) or 0
	absents  = len(atnd.filter(Day_Status = 'Absent'))
	leaves   = len(atnd.filter(Day_Status = 'Leave'))
	half_days  = len(atnd.filter(Day_Status = 'Half Day')) or 0
	presents = presents + (half_days/2)

	total_hours = sum(atnd.filter(Total_Hours__isnull=False).values_list('Total_Hours', flat=True)) or 0
	tot = 0
	
	hdl = DeclareDayAs.objects.filter(Date__month=month, Declare_Day_As='Holiday', Date__year=p.Date.year).order_by('Date')
	hds = [] 
	for pj in hdl:
		hds.append(pj.Date)
	for x in range(1, calendar.monthrange(p.Date.year, month)[1]+1):
		if date(p.Date.year, month, x).strftime('%a') == 'Sun':
			hds.append(date(p.Date.year, month, x))
	hds.sort() if hds != None else hds


	for y in atnd:
		if y.Date in hds and y.Day_Status == 'Present':
			if y.Total_Hours:
				if y.Total_Hours > 7.5:
					y.Total_Hours = y.Total_Hours - 1
				hrs = (y.Total_Hours * 1.5) if y.Total_Hours > 4.5 else y.Total_Hours
			tot = tot + hrs
			presents = presents - 1
		else:
			if y.Total_Hours and y.Total_Hours > 9.5:
				ot = y.Total_Hours-9 
				roundoff = ot - int(ot)
				ot = int(ot)+1 if roundoff*10 >= 5 else int(ot)
			else:
				ot = 0
			tot = tot + ot

	if atnd.last() and atnd.last().Name.Joining_Date:
		allocated_leaves = 24 if atnd.last().Name.Joining_Date <= date(yr, 1, 1) else (12-atnd.last().Name.Joining_Date.month)*(24/12)
	else:
		allocated_leaves = 0
	leaves_left = allocated_leaves - leaves if Monthatnd.objects.filter(Month__month= month-1 if month != 1 else month, Name=p.Name, Month__year=p.Date.year,) != None else allocated_leaves			
	month_atnd = Monthatnd.objects.filter(Month__month=month, Month__year=p.Date.year, Name=p.Name)
	if month_atnd:
		month_atnd.update(Presents=presents, Absents=absents, Leaves=leaves, Leaves_Left=leaves_left, Total_Hours=total_hours, Total_OT=tot, Last_Updated_Date=date.today())
	else:
		month_atnd = Monthatnd.objects.create(Month=date(yr, month, 1), Name=p.Name, Presents=presents, Absents=absents, Leaves=leaves, Leaves_Left=leaves_left, Total_Hours=total_hours, Total_OT=tot, Last_Updated_Date=date.today())
 
	
@login_required
def Expenses_Form(request, proj, fnc, expid):
	pdata = projectname(request, proj)
	if fnc == 'edit' or fnc == 'lock' or fnc == 'unlock' or fnc == 'approvalreq1' or fnc == 'approvalreq0':
		if request.method == 'POST':
			form = ExpensesForm(request.POST, instance=get_object_or_404(Expenses, id=expid))
			if form.is_valid():
				p= form.save()
				p.Submitted_Date = date.today()
				p.save()
				# messages.success(request, "Expenses Has Been Updated successfully")
				url = '/'+str(pdata['pj'])+'/expensesclaimreceipt/apr/edit/'+str(p.id)+'/itemid/'
				return redirect(url)
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect('/%s/expenseslist/expid/'%pdata['pj'])
		else:
			url = '/'+str(pdata['pj'])+'/expensesclaimreceipt/apr/edit/'+str(expid)+'/itemid/'
			if fnc == 'lock':
				Expenses.objects.filter(id=expid).update(Lock_Status=1, Submitted_Date = date.today())
				update_exp_duedays(request, expid)
				return redirect(url)
			elif fnc == 'unlock':
				Expenses.objects.filter(id=expid).update(Lock_Status=0, Submitted_Date = date.today())
				return redirect(url)
			elif fnc == 'approvalreq1':
				exp_apr_update(request, expid)
				messages.success(request, "Expenses Has Been Approved By You successfully")
				url = '/'+str(pdata['pj'])+'/expenseslist/approvalreq/'+str(expid)+'/'
				return redirect(url)
			elif fnc == 'approvalreq0':
				exp = Expenses.objects.filter(id=expid).update(Approval_Status=0)
				Debit_Amounts.objects.get(Expenses=exp).delete()
				messages.success(request, "Expenses Approval Status Has Been Amended to Disapprove")
				url = '/'+str(pdata['pj'])+'/expenseslist/approvalreq/'+str(expid)+'/'
				return redirect(url)
			else:
				return redirect(url)
			form = ExpensesForm(instance=get_object_or_404(Expenses, id=expid))
			return render(request, 'expenses/ExpensesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
	elif fnc == 'delete':
		exp = Expenses.objects.get(id=expid)
		exp.delete()
		messages.success(request, "Expenses Has Been Deleted")
		return redirect('/%s/expenseslist/apr/expid/'%pdata['pj'])
	else:
		if request.method == 'POST':
			form = ExpensesForm(request.POST)
			data_copy = request.POST.items()
			if form.is_valid():
				p= form.save()
				p.Related_Project = pdata['pj']
				p.Submitted_Date = date.today()
				p.Related_Company = CompanyDetails.objects.all().last()
				p.save()
				get_expenses_ref_no(request, p.id)
				# messages.success(request, "Expenses Has Been Submitted successfully")
				url = '/'+str(pdata['pj'])+'/expensesclaimreceipt/apr/edit/'+str(p.id)+'/itemid/'
				return redirect(url)
				# return redirect('/%s/expenseslist/expid/'%pdata['pj'])
			else:				
				messages.error(request, get_errors(request, form.errors))
				form = ExpensesForm(initial=data_copy)
				return render(request, 'expenses/ExpensesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
		else:
			if fnc == 'copy':
				form = ExpensesForm(instance=get_object_or_404(Expenses, id=expid))
				return render(request, 'expenses/ExpensesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
			else:
				form = ExpensesForm()
				form.fields["Sales_Order"].queryset = Orders.objects.filter(Final_Status=0, Related_Project__Short_Name='Services') #load only active and non deleted customers
				return render(request, 'expenses/ExpensesForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})

@login_required
def Expenses_Items_Form(request, proj, fnc, expid, itemid):
	pdata = projectname(request, proj)
	if fnc == 'edit':
		if request.method == 'POST':
			form = ExpensesItemsForm(request.POST, request.FILES, instance=get_object_or_404(Exp_Items, id=itemid))
			if form.is_valid():
				p= form.save()
				update_expense_items(request, expid, p.id)
				exp_update(request, expid)
				# messages.success(request, "Expense Has Been Updated successfully")
				url = '/'+str(pdata['pj'])+'/expensesclaimreceipt/apr/edit/'+expid+'/itemid/'
				return redirect(url)
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect('/%s/expenseslist/expid/'%pdata['pj'])
		else:
			form = ExpensesItemsForm(instance=get_object_or_404(Exp_Items, id=itemid))
			return render(request, 'expenses/ExpensesItemsForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
	elif fnc == 'delete':
		item = Exp_Items.objects.get(id=itemid)
		item.Attach.delete(save=True)
		item.delete()
		item = Exp_Items.objects.filter(Expenses=expid).last()
		itemid = item.id if item != None else None
		update_expense_items(request, expid, itemid)
		exp_update(request, expid)
		# messages.success(request, "Expense Has Been Deleted")
		url = '/'+str(pdata['pj'])+'/expensesclaimreceipt/apr/edit/'+expid+'/itemid/'
		return redirect(url)
	else:
		if request.method == 'POST':
			form = ExpensesItemsForm(request.POST, request.FILES)
			if form.is_valid():
				p= form.save()
				p.save()
				update_expense_items(request, expid, p.id)
				exp_update(request, expid)
				# messages.success(request, "Expense Has Been Added Successfully")
				url = '/'+str(pdata['pj'])+'/expensesclaimreceipt/apr/edit/'+str(expid)+'/itemid/'
				return redirect(url)
			else:				
				return render(request, 'expenses/ExpensesItemsForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
		else:
			form = ExpensesItemsForm()
			return render(request, 'expenses/ExpensesItemsForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})

@login_required
def Expenses_List(request, proj, apr, expid):
	pdata = projectname(request, proj)
	lookup = {'Expenses__Related_Project__isnull':False} if proj == 'All' else {'Expenses__Related_Project':pdata['pj']}
	lookup1 = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	
	if apr != 'approvalreq':
		table = Exp_Items.objects.filter(**lookup).order_by('-Expenses__Submitted_Date')
	else:
		account = Account.objects.get(user=request.user)
		table = Exp_Items.objects.filter(**lookup, Expenses__Approval_Request_To=account, Expenses__Lock_Status=1).order_by('-Expenses__Submitted_Date')	

	# if apr != 'approvalreq':
	# 	table = Expenses.objects.filter(**lookup).order_by('Submitted_Date')
	# else:
	# 	account = Account.objects.get(user=request.user)
	# 	table = Expenses.objects.filter(**lookup, Approval_Request_To=account, Lock_Status=1).order_by('Submitted_Date')	

	filter_data = ExpensesItemsFilter(request.GET, queryset=table)
	has_filter = any(field in request.GET for field in set(filter_data.get_fields()))

	# filter_data = ExpensesFilter(request.GET, queryset=table)
	# has_filter = any(field in request.GET for field in set(filter_data.get_fields()))
	
	table = filter_data.qs
	exp_no = []

	# acnt = Account.objects.all()
	# for a in acnt:
	# 	exp = Expenses.objects.filter(Submitted_By=a, Approval_Status=1, Lock_Status=1).order_by('Submitted_Date')
	# 	for k in exp:
	# 		k.Balance_Amount = k.Total_Amount
	# 		k.Clearing_Status = 0
	# 		Balance_Advance = 0
	# 		k.save()
	# 	deb = Debit_Amounts.objects.filter(Q(Employ=a)|Q(Issued_To=a)).order_by('Issued_Date')
	# 	deb.update(As_Advance=0)

	
	for x in table:
		exp_no.append(Expenses.objects.get(Reference_No=x.Expenses.Reference_No))
	exp = list(dict.fromkeys(exp_no))
	
	# if has_filter: #update filter data queyset
	# 	for x in table:
	# 		exp_no.append(Expenses.objects.get(Reference_No=x.Expenses.Reference_No))
	# 	exp = list(dict.fromkeys(exp_no))
	# else:
	# 	exp = []
	# 	for x in Expenses.objects.filter(**lookup1).order_by('Submitted_Date'): exp.append(x)
	print(exp)
	cat_list = []
	for x in exp:
		cat = []
		items = Exp_Items.objects.filter(Expenses=x)
		for y in items:
			cat.append(y.Category)
		cat = list(dict.fromkeys(cat))
		cat_list.append(cat)
	data = zip(exp, cat_list)

	total, due, paid = 0, 0, 0

	for x in exp: total = total+x.Total_Amount if x.Total_Amount != None else 0
	for x in exp: due = due + x.Balance_Amount if x.Balance_Amount != None and x.Balance_Amount > 0 else due
	for x in exp: paid = paid + x.Total_Amount - x.Balance_Amount if x.Total_Amount != None and x.Balance_Amount != None and x.Balance_Amount >= 0 else x.Total_Amount if x.Total_Amount != None else 0
	cats1 = ['Travel','Food','Lodging','Fuel','Transportation','Recharges','Stationery','General Purchase','Miscellaneous']
	cats = []
	val = []
	for x in cats1:
		cat_total = 0
		cat_total = cat_total + (sum(table.filter(Category=x).values_list('Amount', flat=True)) or 0)
		if cat_total != 0:
			cats.append(x)
			val.append(cat_total)
	against = zip(cats, val)
	t_req = len(exp)
	apr_req, p_req, apr_req_val, p_req_val = 0,0,0,0
	for x in exp:		
		if x.Approval_Status == 1:
			apr_req, apr_req_val = apr_req+1, apr_req_val+x.Total_Amount if x.Total_Amount != None else 0
		else:
			p_req, p_req_val = p_req+1, p_req_val+x.Total_Amount if x.Total_Amount != None else 0 

	claims = {'total':total, 'due':due, 'paid':paid, 'against':against}
	req = {'t_req':t_req, 'apr_req':apr_req, 'p_req':p_req, 'apr_req_val':apr_req_val, 'p_req_val':p_req_val}		
	return render(request, 'expenses/ExpensesList.html', {'data':data, 'pdata':pdata, 'filter_data':filter_data, 'claims':claims, 'apr':apr, 'req':req})

@login_required
def Expenses_Receipt(request, proj, apr, fnc, expid, itemid):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	exp = Expenses.objects.get(id=expid)
	items = Exp_Items.objects.filter(Expenses=exp).order_by('From_Date')
	if itemid != 'itemid':
		fnc = 'edit'
		form_item = ExpensesItemsForm(instance=get_object_or_404(Exp_Items, id=itemid))
	else:
		fnc=''
		form_item = ExpensesItemsForm()
	form_exp = ExpensesForm(instance=get_object_or_404(Expenses, id=expid))
	amount_in_words =  num2words(int(exp.Balance_Amount), to='cardinal', lang='en_IN') if exp.Balance_Amount else None
	return render(request, 'docformats/ExpensesReceipt.html', {'exp':exp, 'pdata':pdata, 'items':items, 
		'item_id':itemid, 'form':form_item, 'form_exp':form_exp, 'amount_in_words':amount_in_words, 'fnc':fnc, 'apr':apr})

@login_required
def Exp_Approval_Req(request, proj, apr, expid):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	exp = Expenses.objects.get(id=expid)
	items = Exp_Items.objects.filter(Expenses=exp)
	form_exp = ExpensesForm(instance=get_object_or_404(Expenses, id=expid))
	amount_in_words =  num2words(int(exp.Balance_Amount), to='cardinal', lang='en_IN') if exp.Balance_Amount else None
	return render(request, 'docformats/ExpensesReceipt.html', {'exp':exp, 'pdata':pdata, 'items':items, 
		'item_id':itemid, 'form':form_item, 'form_exp':form_exp, 'amount_in_words':amount_in_words, 'fnc':fnc, 'apr':apr})


@login_required
def Debit_Form(request, proj, fnc, did):
	pdata = projectname(request, proj)
	if fnc == 'edit':
		if request.method == 'POST':
			form = IssuedAmountsForm(request.POST, request.FILES, instance=get_object_or_404(Debit_Amounts, id=did))
			if form.is_valid():
				p= form.save()				
				if p.Related_To != 'Salary Advance':
					update_debits(request, p.id, fnc)
				else:
					p.Employ = p.Issued_To
					p.save()
					sal_adv = Salary_Advances.objects.filter(Employ=p.Employ).last()
					print(sal_adv)
					if sal_adv:
						sal_adv = sal_adv.Advance+p.Issued_Amount if sal_adv.Advance != None else p.Issued_Amount
						sal_adv.Issued_By, sal_adv.Issued_Date = p.Issued_By, p.Issued_Date
						sal_adv.save()
					else:
						Salary_Advances.objects.create(Employ=p.Employ, Advance=p.Issued_Amount, Issued_By=p.Issued_By, Issued_Date = p.Issued_Date)
				messages.success(request, "Debit Details Has Been Updated successfully")
				return redirect('/%s/debitlist/'%pdata['pj'])
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect('/%s/debitlist/'%pdata['pj'])
		else:
			form = IssuedAmountsForm(instance=get_object_or_404(Debit_Amounts, id=did))
			return render(request, 'expenses/DebitForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
	elif fnc == 'delete':
		df = Debit_Amounts.objects.get(id=did)
		amount = df.Issued_Amount
		empl = df.Employ if df.Employ != None else None
		
		if df.Related_To == 'Salary Advance':
			sal_adv = Salary_Advances.objects.filter(Employ=empl)
			if sal_adv:
				sal_adv = sal_adv.Advance - amount if sal_adv.Advance != None else amount
				sal_adv = 0 if sal_adv < 0 else sal_adv
				sal_adv.save()
				df.delete()
				messages.success(request, "Debit Details Has Been Deleted")
				return redirect('/%s/debitlist/'%pdata['pj'])
		if df.Expenses:
			expid = df.Expenses.id
		else:
			expid = None
		df.delete()
		delete_debit(request, amount, expid, empl)
		messages.success(request, "Debit Details Has Been Deleted")
		return redirect('/%s/debitlist/'%pdata['pj'])
	else:
		if request.method == 'POST':
			form = IssuedAmountsForm(request.POST, request.FILES)
			if form.is_valid():
				n = get_debitvoucher_num(request, Debit_Amounts.objects.all().last())	
				p= form.save(commit=False)
				if p.Paid_To == 'Against Expenses':
					if not p.Expenses:
						messages.error(request, 'Please Choose Expenses If You Select Against Expenses. Try Again')
						return redirect('/%s/debitlist/'%pdata['pj'])
				if p.Paid_To == 'As Advance To Staff':
					if not p.Employ:
						messages.error(request, 'Please Choose Employ If You Select As Advance To Staff. Try Again')
						return redirect('/%s/debitlist/'%pdata['pj'])
				p.Voucher_No = n
				p.save()
				p.Related_Project = pdata['pj']
				p.Related_Company = CompanyDetails.objects.all().last()
				p.save()
				if p.Related_To != 'Salary Advance':
					update_debits(request, p.id, fnc)
				else:
					p.Employ = p.Issued_To
					p.save()
					sal_adv = Salary_Advances.objects.filter(Employ=p.Employ).last()
					if sal_adv:
						sal_adv = sal_adv.Advance+p.Issued_Amount if sal_adv.Advance != None else p.Issued_Amount
						sal_adv.Issued_By, sal_adv.Issued_Date = p.Issued_By, p.Issued_Date
						sal_adv.save()
					else:
						Salary_Advances.objects.create(Employ=p.Employ, Advance=p.Issued_Amount, Issued_By=p.Issued_By, Issued_Date = p.Issued_Date)
				messages.success(request, "Debit Details Has Been Added Successfully")
				return redirect('/%s/debitlist/'%pdata['pj'])
			else:				
				return render(request, 'expenses/DebitForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
		else:
			form = IssuedAmountsForm()
			form.fields["Expenses"].queryset = Expenses.objects.filter(Balance_Amount__gt=0, Approval_Status=1) #load only active and non deleted customers
			return render(request, 'expenses/DebitForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})

@login_required 
def Debit_List(request, proj):
	pdata = projectname(request, proj)	
	lookup = {'Related_Project__isnull':False} if proj == 'All' else {'Related_Project':pdata['pj']}
	table = Debit_Amounts.objects.filter(**lookup).order_by('-Voucher_No')
	
	filter_data = DebitFilter(request.GET, queryset=table)
	table = filter_data.qs

	if filter_data.form.cleaned_data.get('Employ'):
		employfilter = filter_data.form.cleaned_data.get('Employ')
	else:
		employfilter = 0

	empl_list = []
	for x in table:
		if x.Employ:
			empl_list.append(x.Employ)
	empl_list = list(dict.fromkeys(empl_list))

	print(empl_list)

	# for x in Debit_Amounts.objects.all():
	# 	update_debits(request, x.id, 'create')
	# return HttpResponse('kk')

	total, staff, outside, advances, exp_adv, sal_adv = 0,0,0,0,0,0
	if table:
		total = sum(table.values_list('Issued_Amount', flat=True)) or 0
		for x in empl_list:
			e1 = Staff_Advances.objects.filter(Employ=x).last()
			exp_adv = (exp_adv + e1.Advance) if e1 != None and e1.Advance != None else exp_adv
			e2 = Salary_Advances.objects.filter(Employ=x).last()
			sal_adv = (sal_adv + e2.Advance) if e2 != None and e2.Advance != None else sal_adv
		for x in table:
			if x.Employ:
				staff = staff + x.Issued_Amount if x.Issued_Amount != None else 0
			else:
				outside = outside + x.Issued_Amount if x.Issued_Amount != None else 0
				if x.Issued_Amount and x.Amount_to_be_Pay:
					if x.Issued_Amount > x.Amount_to_be_Pay:
						advances = advances + x.Issued_Amount - x.Amount_to_be_Pay
	df = {'total':total, 'staff':staff, 'outside':outside, 'advances':advances, 'exp_adv':exp_adv, 'sal_adv':sal_adv}
	
	return render(request, 'expenses/DebitList.html', {'table': table, 'filter_data':filter_data, 'pdata':pdata, 'df':df, 'employfilter':employfilter})

@login_required
def Debit_Receipt(request, proj, did):
	pdata = projectname(request, proj)	
	exp = Debit_Amounts.objects.get(id=did)
	amount_in_words =  num2words(int(exp.Issued_Amount), to='cardinal', lang='en_IN')
	return render(request, 'docformats/DebitReceipt.html', {'exp': exp, 'pdata':pdata, 'words':amount_in_words})

@login_required
def Attendance_Form(request, proj, fnc, eid, returnpage):
	pdata = projectname(request, proj)
	if fnc == 'edit':
		if request.method == 'POST':
			form = AttendanceForm1(request.POST, instance=get_object_or_404(Attendance, id=eid))
			if form.is_valid():
				p= form.save()
				p.Is_Manual = True
				p.save()
				if p.Day_Status == 'Absent' or p.Day_Status == 'Leave':
					p.Start_Time, p.End_Time, p.Total_Hours = None, None, None
					p.save()
					update_month_atnd(request, p.id)
				if p.End_Time:
					update_month_atnd(request, p.id)
				messages.success(request, "Attendance for the Selected Emoploy Has Been Updated Successfully")
				url = '/'+str(pdata['pj'])+'/daywiseattendancelist/'+str(p.Date)+'/' if returnpage == 'daywise' else '/'+str(pdata['pj'])+'/employwiseattendance/'+str(p.Date.strftime('%Y-%m'))+'/'+p.Name.Name+'/'
				return redirect(url)
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect('/%s/daywiseattendancelist/day/'%pdata['pj'])
		else:
			form = AttendanceForm(instance=get_object_or_404(Attendance, id=eid))
			form.fields["Sales_Order"].queryset = Orders.objects.filter(Final_Status=0) 
			return render(request, 'attendance/AttendanceForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
	elif fnc == 'delete':
		atnd = Attendance.objects.get(id=eid)
		dt = atnd.Date
		empl = atnd.Name
		atnd.delete()
		atnd = Attendance.objects.filter(Name=empl).order_by('Date').last()
		update_month_atnd(request, atnd.id) if atnd != None else None
		messages.success(request, "Attendance for the Selected Emoploy Has Been Deleted")
		if returnpage == 'employwise':
			dt = str(dt.strftime('%Y-%m'))
			url = '/'+str(pdata['pj'])+'/employwiseattendance/'+dt+'/'+empl.Name+'/'
		else:
			url = '/'+str(pdata['pj'])+'/daywiseattendancelist/day/'
		return redirect(url)
	else:
		if request.method == 'POST':
			form = AttendanceForm(request.POST)
			data_copy = request.POST.items()
			if form.is_valid():
				p= form.save(commit=False)
				atnd = Attendance.objects.filter(Date=p.Date)
				if atnd:
					for x in atnd: 
						if p.Name == x.Name:
							messages.error(request, "Employ Attendance Already Registered, Please Check Employ Name Again")
							form = AttendanceForm(initial=data_copy)
							return render(request, 'attendance/AttendanceForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})

				p.Issued_By = Account.objects.get(user=request.user)
				
				if p.Day_Status == 'Absent' or p.Day_Status == 'Leave':
					p.Start_Time, p.End_Time, p.Total_Hours = None, None, None
					p.save()
					update_month_atnd(request, p.id)
				p.Is_Manual = True
				p.save()
				if p.End_Time:
					update_month_atnd(request, p.id)
				
				messages.success(request, "Attendance for the Selected Emoploy Has Been Added Successfully")
				url = '/'+str(pdata['pj'])+'/daywiseattendancelist/'+str(p.Date)+'/'
				return redirect(url)
			else:				
				return render(request, 'attendance/AttendanceForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
		else:
			if fnc == 'copy':
				form = AttendanceForm1(instance=get_object_or_404(Attendance, id=eid))
				form.fields["Sales_Order"].queryset = Orders.objects.filter(Final_Status=0) 
				return render(request, 'attendance/AttendanceForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
			else:
				form = AttendanceForm(initial={'Date':date.today(), 'Start_Time':datetime.now().time().strftime("%H:%M")})
				form.fields["Sales_Order"].queryset = Orders.objects.filter(Final_Status=0, Related_Project__Short_Name='Services') 
				return render(request, 'attendance/AttendanceForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})

@login_required
def Holidays_Form(request, proj, fnc, hid):
	pdata = projectname(request, proj)
	if fnc == 'edit':
		if request.method == 'POST':
			form = DeclareDayAsForm(request.POST, instance=get_object_or_404(DeclareDayAs, id=hid))
			if form.is_valid():
				p= form.save()
				messages.success(request, "Details Has Been Updated Successfully")
				return redirect('/%s/holidayslist/year/'%pdata['pj'])
			else:
				messages.error(request, get_errors(request, form.errors))
				return redirect('/%s/holidayslist/year/'%pdata['pj'])
		else:
			form = DeclareDayAsForm(instance=get_object_or_404(DeclareDayAs, id=hid))
			return render(request, 'attendance/HolidaysForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
	elif fnc == 'delete':
		data = DeclareDayAs.objects.get(id=hid)
		data.delete()
		return redirect('/%s/holidayslist/year/'%pdata['pj'])
	else:
		if request.method == 'POST':
			form = DeclareDayAsForm(request.POST)
			# data_copy = request.POST.items()
			if form.is_valid():
				p= form.save()
				messages.success(request, "Details Has Been Added Successfully")
				return redirect('/%s/holidayslist/year/'%pdata['pj'])
			else:				
				return render(request, 'attendance/HolidaysForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
		else:
			if fnc == 'copy':
				form = DeclareDayAsForm1(instance=get_object_or_404(DeclareDayAs, id=hid))
				return render(request, 'attendance/HolidaysForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
			else:
				form = DeclareDayAsForm()
				return render(request, 'attendance/HolidaysForm.html', {'form': form, 'pdata':pdata, 'fnc':fnc})

# @login_required
# def DayWise_Attendance(request, proj, day):
# 	pdata = projectname(request, proj)
# 	dt = date.today() if day == 'day' else day
# 	table = Attendance.objects.filter(Date=dt).order_by('id')

# 	filter_data = AttendanceFilter(request.GET, queryset=table)
# 	table = filter_data.qs
	
# 	presents, leaves, absents, od = 0,0,0,0
# 	presents = len(table.filter(Day_Status = 'Present'))
# 	absents = len(table.filter(Day_Status = 'Absent'))
# 	leaves = len(table.filter(Day_Status = 'Leave'))
# 	od = len(table.filter(Q(Day_Status = 'On Duty')|Q(Day_Status = 'Tour')))
# 	ot = []
# 	for x in table:
# 		if x.Total_Hours and x.Total_Hours > 9.5:
# 			ot.append(x.Total_Hours-9)
# 		else:
# 			ot.append(None)
# 	data = zip(table, ot)
# 	df = {'presents':presents, 'absents':absents, 'leaves':leaves, 'od':od}
# 	if not table:
# 		messages.error(request, 'Attendance Not Registered/Available for Requested Date/Employ')
# 	return render(request, 'attendance/DayWiseAttendance.html', {'day': day, 'pdata':pdata, 'table':table, 'filter_data':filter_data, 'df':df, 'data':data})

@login_required
def MonthWise_Attendance(request, proj, month):
	pdata = projectname(request, proj)
	dt = date.today() 
	month = date.today()  if month == 'month' else (datetime.strptime(month, '%Y-%m'))
	m = month.strftime('%Y-%m')

	if month.month == date.today().month:
		month = date.today()

	if month.month > date.today().month and month.year >= date.today().year:
		messages.error(request, "Please Choose Less Than or Equal to Current Month for Monthly Attendance")
		return render(request, 'attendance/MonthWiseAttendance.html', {'month': month, 'm':m, 'pdata':pdata})
	
	if not Attendance.objects.filter(Date__month=month.month, Date__year=month.year) or not Monthatnd.objects.filter(Month__month=month.month, Month__year=month.year):
		messages.error(request, "Daily Attendance Not Available for Selected Month to Generate Monthly Attendance Report")
		return render(request, 'attendance/MonthWiseAttendance.html', {'month': month, 'm':m, 'pdata':pdata})
	
	k = working_days(request, month)

	monthatnds = Monthatnd.objects.filter(Month__month=month.month, Month__year=month.year)
	table = Attendance.objects.filter(Date__month=month.month, Date__year=month.year).order_by('Name__Employee_Id')
	filter_data = AttendanceFilter(request.GET, queryset=table)
	table = filter_data.qs

	if filter_data.form.cleaned_data.get('Sales_Order'):
		orderfilter = filter_data.form.cleaned_data.get('Sales_Order')
	else:
		orderfilter = 0

	print(orderfilter)

	empl_list = []
	if orderfilter == 0:
		for x in monthatnds:
			empl_list.append(x.Name)
	else:
		for x in table:
			empl_list.append(x.Name)
		empl_list = list(dict.fromkeys(empl_list))

	if month.month == dt.month:
		eDate = date.today().day
	else:
		eDate = calendar.monthrange(month.year, month.month)[1]

	dt_list, dates_list, daily_atnd, month_atnd, presents, leaves, absents, ot, hds = [],[],[],[],[],[],[],[],[]
	hdl = DeclareDayAs.objects.filter(Date__month=month.month, Declare_Day_As='Holiday', Date__year=month.year).order_by('Date')
	 
	for p in hdl:
		hds.append(p.Date)
	
	for x in range(1, eDate+1):
		dt_list.append(x)
		dates_list.append(date(month.year, month.month, x).strftime('%Y-%m-%d'))
		if date(month.year, month.month, x).strftime('%a') == 'Sun':
			hds.append(date(month.year, month.month, x))

	hds.sort() if hds != None else hds

	for x in empl_list:
		if orderfilter == 0:
			atnd = Attendance.objects.filter(Name=x, Date__month=month.month, Date__year=month.year)
			m_atnd = Monthatnd.objects.filter(Name=x, Month__month=month.month, Month__year=month.year).last()
		else:
			atnd = Attendance.objects.filter(Name=x, Date__month=month.month, Date__year=month.year, Sales_Order=orderfilter)
			if month.month == dt.month and month.year == dt.year:
				m_atnd = None
			else:
				m_atnd = Monthatnd.objects.filter(Name=x, Month__month=month.month, Month__year=month.year).last()
		# atnd = Attendance.objects.filter(Name=x, Date__month=month.month, Date__year=month.year)
		# m_atnd = Monthatnd.objects.filter(Name=x, Month__month=month.month, Month__year=month.year).last()
		# presents, leaves, absents, ot = len(atnd.filter(Day_Status='Present')), len(atnd.filter(Day_Status='Leave')), len(atnd.filter(Day_Status='Absent')), sum(atnd.values_list('T'))
		d_atnd = []
		ot = []
		# daily_atnd = []
		if (atnd and m_atnd) or (atnd != None and orderfilter != 0):
			for a in dt_list:
				s = atnd.filter(Date__day=a).last()
				if s:
					if s.Date in hds and s.Day_Status == 'Present':
						if s.Total_Hours:
							if s.Total_Hours > 7.5:
								s.Total_Hours = s.Total_Hours - 1
							hrs = (s.Total_Hours * 1.5) if s.Total_Hours > 4.5 else s.Total_Hours
						d_atnd.append('OT'+str(int(hrs)))
						ot.append(0)
					elif s.Day_Status == 'Present':
						oth = 0
						d_atnd.append('P')
						if s.Total_Hours and s.Total_Hours > 9.5:
							oth = s.Total_Hours-9 
							roundoff = oth - int(oth)
							oth = int(oth)+1 if roundoff*10 >= 5 else int(oth)
						else:
							oth = 0
						ot.append(oth)
					elif s.Day_Status == 'Leave':
						d_atnd.append('L')
						ot.append(0)
					elif s.Day_Status == 'Absent':
						d_atnd.append('A')
						ot.append(0)
					elif s.Day_Status == 'Half Day':
						d_atnd.append('HF')
						ot.append(0)
					else:
						d_atnd.append('')
						ot.append(0)
				else:
					ot.append(0)
					if date(month.year, month.month, a) in hds:
						d_atnd.append('HD')
					else:
						d_atnd.append('NR') if orderfilter == 0 else d_atnd.append('') #not mentioned
			dat = zip(d_atnd, dates_list, ot)
			daily_atnd.append(dat)
			# daily_atnd.append(d_atnd)
			month_atnd.append(m_atnd)
		else:
			for x in dates_list:
				d_atnd.append(None)
				ot.append(0)
			dat = zip(d_atnd, dates_list, ot)
			daily_atnd.append(dat)
			# daily_atnd.append(None)
			month_atnd.append(None)

	data = zip(empl_list, daily_atnd, month_atnd)
		
	if month.month != date.today().month and month.year <= date.today().year:
		dates = None
	else: 
		month = None
		dates = {'start':date(date.today().year, date.today().month, 1), 'end':date.today()}
	
	return render(request, 'attendance/MonthWiseAttendance.html', {'data':data, 'dt_list':dt_list, 'month': month, 'dates':dates, 'pdata':pdata, 
		'filter_data':filter_data, 'workdays':k, 'workhours1':(k*9)+(k*9*0.05), 'workhours2':(k*9)-(k*9*0.05), 'order':orderfilter, 'm':m})

@login_required
def DayWise_Attendance(request, proj, day):
	pdata = projectname(request, proj)
	dt = date.today() if day == 'day' else day
	table = Attendance.objects.filter(Date=dt).order_by('id')
	filter_data = AttendanceFilter(request.GET, queryset=table)
	table = filter_data.qs
	presents, leaves, absents, od = 0,0,0,0
	presents = len(table.filter(Day_Status = 'Present'))
	absents = len(table.filter(Day_Status = 'Absent'))
	leaves = len(table.filter(Day_Status = 'Leave'))
	od = len(table.filter(Q(Day_Status = 'On Duty')|Q(Day_Status = 'Tour')))
	ot = []
	for x in table:
		if x.Total_Hours and x.Total_Hours > 9.5:
			ot.append(x.Total_Hours-9)
		else:
			ot.append(None)
	data = zip(table, ot)
	df = {'presents':presents, 'absents':absents, 'leaves':leaves, 'od':od}
	if not table:
		messages.error(request, 'Attendance Not Registered/Available for Requested Date/Employ')
	employes = Account.objects.filter(Status=1, ds=1).order_by('Employee_Id')
	return render(request, 'attendance/DayWiseAttendance.html', {'day': day, 'pdata':pdata, 'table':table, 'filter_data':filter_data, 'df':df, 'data':data, 'employes':employes, 'month':dt})

@login_required
def Employ_Wise_Attendance(request, proj, month, empl):
	pdata = projectname(request, proj)
	initail_month = month
	month = date.today()  if month == 'month' else (datetime.strptime(month, '%Y-%m'))

	if empl == 'noemploy':
		messages.error(request, 'Please Choose Correct Employ Details')
		return redirect('/%s/daywiseattendancelist/day/'%pdata['pj'])
	
	atnd = Attendance.objects.filter(Date__month=month.month, Date__year=month.year, Name__Name=empl).order_by('Date')
	employ = Account.objects.filter(Name=empl).last()
	employes = Account.objects.filter(Status=1, ds=1).order_by('Employee_Id')

	if month.month > date.today().month and month.year >= date.today().year:
		messages.error(request, "Please Choose Less Than or Equal to Current Month")
		return redirect('/%s/daywiseattendancelist/day/'%pdata['pj'])

	if not atnd:
		messages.error(request, 'No Attendance Available for Selected Month for Selected Employ')
		return render(request, 'attendance/EmployWiseAttendance.html', {'month': month, 'pdata':pdata, 'table':atnd, 'employ':employ, 'employes':employes})
	
	k = working_days(request, month)
	workingdays = Working_Days.objects.filter(Month__month=month.month, Month__year=month.year).last()
	workingdays = workingdays.Working_Days if workingdays != None else 0
	presents, leaves, absents, leaves_left = 0,0,0,0
	presents = len(atnd.filter(Day_Status = 'Present'))
	absents = len(atnd.filter(Day_Status = 'Absent'))
	leaves = len(atnd.filter(Day_Status = 'Leave'))
	leaves_left = Monthatnd.objects.filter(Month__month=month.month, Month__year=month.year, Name__Name=empl)

	df = {'presents':presents, 'absents':absents, 'leaves':leaves, 'workingdays':workingdays, 'leaves_left':leaves_left}
	
	if month.month != date.today().month and month.year <= date.today().year:
		dates = None
	else: 
		month = None
		dates = {'start':date(date.today().year, date.today().month, 1), 'end':date.today()}
	
	return render(request, 'attendance/EmployWiseAttendance.html', {'month': month, 'dates':dates, 'pdata':pdata, 'table':atnd, 'employ':employ, 'df':df, 'employes':employes})

@login_required
def Holidays_List(request, proj, year):
	pdata = projectname(request, proj)
	year = date.today().year  if year == 'year' else year
	table = DeclareDayAs.objects.filter(Date__year=year).order_by('-Date')
	if not table:
		messages.error(request, 'No Data Available for Your Requested Year')
	return render(request, 'attendance/HolidaysList.html', {'pdata':pdata, 'table':table, 'year':year})

@login_required
def Gen_Auto_Attendance(request, proj, month):
	pdata = projectname(request, proj)
	month = date.today()  if month == 'month' else (datetime.strptime(month, '%Y-%m'))
	empls = Account.objects.filter(ds=1, Status=1).order_by('Sr_No')

	if month.month == date.today().month:
		month = date.today()
	
	if month.month == date.today().month and month.year == date.today().year:
		eDate = date.today().day
	else:
		eDate = calendar.monthrange(month.year, month.month)[1]
	month_dates = []
	for d in range(eDate):
		if date(month.year, month.month, 1+d).strftime('%a') != 'Sun':
			month_dates.append(date(month.year, month.month, 1+d).strftime('%Y-%m-%d'))
	
	holidays = DeclareDayAs.objects.filter(Q(Date__month=month.month,  Date__year=month.year, Declare_Day_As='Holiday', Date__lte=date.today())|Q(Date__month=month.month,  Date__year=month.year, Declare_Day_As='Half Day', Date__lte=date.today())).order_by('Date')
	hds=[]
	for x in holidays:
		hds.append((x.Date).strftime('%Y-%m-%d'))
	if hds:
		for d in hds:
			if d in month_dates:
				month_dates.remove(d)

	extra_work_days = DeclareDayAs.objects.filter(Date__month=month.month, Date__year=month.year, Declare_Day_As='Working Day', Date__lte=date.today()).order_by('Date')
	ewd = []
	for x in extra_work_days:
		ewd.append((x.Date).strftime('%Y-%m-%d'))
	if ewd:
		for d in ewd:
			month_dates.append(d)
	month_dates.sort()
		
	for e in empls:
		dates = month_dates.copy()
		atnd = Attendance.objects.filter(Name=e, Date__month=month.month, Date__year=month.year)
		if  atnd:
			for d in atnd:
				if (d.Date).strftime('%Y-%m-%d') in month_dates:
					dates.remove((d.Date).strftime('%Y-%m-%d'))
		if dates != []:
			for x in dates:
				Attendance.objects.create(Name=e, Date=x, Start_Time='09:00:00', End_Time='18:00:00', Total_Hours=9, Day_Status='Present', Issued_By=Account.objects.get(user=request.user), Is_Manual=False)
		if hds:
			for h in hds:
				atnd = Attendance.objects.filter(Name=e, Date__month=month.month, Date__year=month.year, Date=h)
				if atnd:
					atnd.delete()
		if ewd:
			for w in ewd:
				atnd = Attendance.objects.filter(Name=e, Date__month=month.month, Date__year=month.year, Date=w)
				if atnd:
					pass
				else:
					Attendance.objects.create(Name=e, Date=w, Start_Time='09:00:00', End_Time='18:00:00', Total_Hours=9, Day_Status='Present', Issued_By=Account.objects.get(user=request.user), Is_Manual=False)


		update_month_atnd(request, Attendance.objects.filter(Name=e, Date__month=month.month, Date__year=month.year).last().id)		
		
	url = '/'+str(pdata['pj'])+'/monthwiseattendancelist/'+month.strftime('%Y-%m')+'/'
	return redirect(url)

def call_extra_work_days_sal(request, month, a):
	atnd = Attendance.objects.filter(Q(Name=a, Date__month=month.month, Date__year=month.year)|Q(Day_Status='Half Day'))
	e_sal = Empl_Salaries.objects.filter(Employ_Name=a).last()
	presents = []
	hrs = 0
	for d in atnd:
		presents.append(d.Date)
		if (d.Date).strftime('%a') == 'Sun':
			if d.Total_Hours:
				if d.Total_Hours > 7.5:
					d.Total_Hours = d.Total_Hours - 1
				hrs = hrs + (d.Total_Hours * 1.5) if d.Total_Hours > 4.5 else (hrs + d.Total_Hours)

				
	hds = []
	hd = DeclareDayAs.objects.filter(Date__month=month.month, Date__year=month.year, Declare_Day_As='Holiday')
	if hd:
		for x in hd:
			hds.append(x.Date)
	for dt in hds:
		if dt in presents:
			d = Attendance.objects.filter(Name=a, Date=dt).last()
			if d.Total_Hours:
				if d.Total_Hours > 7.5:
					d.Total_Hours = d.Total_Hours - 1
				hrs = hrs + (d.Total_Hours * 1.5) if d.Total_Hours > 4.5 else (hrs + d.Total_Hours)
	return hrs

	# d1 = date(month.year, month.month, 1)
	# d2 = date(month.year, month.month, calendar.monthrange(month.year, month.month)[1])
	# delta = d2 - d1
	# for i in range(calendar.monthrange(month.year, month.month)[1]):
	#     if (d1 + timedelta(days=i)).strftime('%a') == 'Sun':
	#     	hds.append(d1 + timedelta(days=i))
	

@login_required
def Gen_Monthly_Salaries(request, proj, month, mode):
	pdata = projectname(request, proj)
	dt = date.today()
	sal = None

	url = '/'+str(pdata['pj'])+'/monthlysalaries/month/select/'

	if month != 'month':
		try:
			month = datetime.strptime(month, '%Y-%m')
			mnth = datetime.strftime(month, '%Y-%m')
			m = month.month
		except:
			messages.error(request, 'Please Select Proper Month Format')
			return render(request, 'expenses/MonthlySalaries.html', {'month': 'month', 'pdata':pdata, 'table':sal, 'mode':'select'})

		if month.year > dt.year or (month.year == dt.year and month.month > dt.month ) :
	 		messages.error(request, 'Current Month Not Completed to Generate Salaries')
	 		return render(request, 'expenses/MonthlySalaries.html', {'month': 'month', 'pdata':pdata, 'table':sal, 'mode':'select'})

	if mode == 'select':
		return render(request, 'expenses/MonthlySalaries.html', {'month': 'month', 'pdata':pdata, 'table':sal, 'mode':'select'})
	
	if month == 'month' and mode == 'get':
		messages.error(request, 'Please Select Month To Get Salaries')
		return render(request, 'expenses/MonthlySalaries.html', {'month': 'month', 'pdata':pdata, 'table':sal, 'mode':'select'})

	m_atnd = Monthatnd.objects.filter(Month__month=m, Month__year=month.year)

	if not m_atnd:
		messages.error(request, 'Kindly Generate Attendance for the Requested Month Before Generate/Get Salaries')
		return render(request, 'expenses/MonthlySalaries.html', {'month': 'month', 'pdata':pdata, 'table':sal, 'mode':'select'})

	sal = Monthly_Salaries.objects.filter(Month__month=m, Month__year=month.year)
	empls = Account.objects.filter(Status=1, ds=1).order_by('Sr_No')
	k = calendar.monthrange(month.year, month.month)[1]
	k = k - sum(1 for week in calendar.monthcalendar(month.year,month.month) if week[-1])

	if mode == 'regen':
		if sal:
			sal.delete()
			sal = Monthly_Salaries.objects.filter(Month__month=m, Month__year=month.year)

	if sal and mode == 'gen':
		messages.error(request, 'Selected Month Salaries Already Generated')
		return render(request, 'expenses/MonthlySalaries.html', {'month': mnth, 'month1':month, 'pdata':pdata, 'table':sal, 'wd':k, 'mode':mode})

	if mode == 'delete':
		if sal:
			sal.delete()
			messages.success(request, 'Selected Month Salaries Has Been Deleted')
			return render(request, 'expenses/MonthlySalaries.html', {'month': 'month', 'pdata':pdata, 'table':sal, 'mode':'select'})

	if sal:
		if mode == 'get':
			return render(request, 'expenses/MonthlySalaries.html', {'month': mnth, 'month1':month, 'pdata':pdata, 'table':sal, 'wd':k, 'mode':'get'}) 
	else:
		if mode == 'gen' or mode == 'regen':
			if m == dt.month:
			 	if dt.day < 25:
			 		messages.error(request, 'Current Month Not Completed to Generate Salaries')
			 		return render(request, 'expenses/MonthlySalaries.html', {'month': mnth, 'month1':month, 'pdata':pdata, 'table':sal, 'wd':k, 'mode':mode})

			for a in empls:
				atnd = Monthatnd.objects.filter(Name=a, Month__month=m, Month__year=month.year).last()
				e_sal = Empl_Salaries.objects.filter(Employ_Name=a).last()
				if atnd:
					if e_sal:
						i_wd = atnd.Presents + atnd.Leaves
						i_wd = k if i_wd > k else i_wd
						hrs = call_extra_work_days_sal(request, month, a) if e_sal.OT_Eligibility == 1 else 0
						i_sal = e_sal.Gross_Salary*i_wd/k
						i_esi, i_pf = e_sal.ESI_Amount*(i_wd if i_wd < 26 else 26)/26 if e_sal.ESI_Eligibility == 1 else 0 , e_sal.PF_Amount*(i_wd if i_wd < 26 else 26)/26 if e_sal.PF_Eligibility == 1 else 0
						i_net = i_sal - i_esi - i_pf - (e_sal.Professional_Tax if e_sal.Professional_Tax != None else 0)
						i_lop = e_sal.Net_Salary - i_net
						i_lop = i_lop if i_lop >= 0 else 0
						i_ot = (((e_sal.Gross_Salary/k/8)*((atnd.Total_OT+hrs) if atnd.Total_OT != None else 0)) if e_sal.OT_Eligibility == 1 else 0) 
						i_net = i_net + i_ot 
						gen_sal = Monthly_Salaries.objects.create(Name=a, Month=date(month.year, m, 1), Presents=i_wd, Issued_Salary=int(i_net),
						PF=int(i_pf), ESI=int(i_esi), OT_Amount=int(i_ot), Professional_Tax=e_sal.Professional_Tax, LOP=int(i_lop))

	if mode == 'gen':
		messages.success(request, 'Requested Month Salaries Has Been Generated')
	if mode == 'regen':
		messages.success(request, 'Requested Month Salaries Has Been Re-Generated Again')

	sal = Monthly_Salaries.objects.filter(Month__month=m, Month__year=month.year)

	return render(request, 'expenses/MonthlySalaries.html', {'month': mnth, 'month1':month, 'pdata':pdata, 'table':sal, 'wd':k, 'mode':'get'})


@login_required
def Monthly_Salaries_Edit(request, proj, month, eid):
	pdata = projectname(request, proj)
	url = '/'+str(pdata['pj'])+'/monthlysalaries/'+month+'/get/'
	if request.method == 'POST':
		form = EmployMonthlySalaryForm(request.POST, instance=get_object_or_404(Monthly_Salaries, id=eid))
		if form.is_valid():
			p= form.save()
			messages.success(request, "Details Has Been Updated Successfully")
			return redirect(url)
		else:
			messages.error(request, get_errors(request, form.errors))
			return redirect(url)
	else:
		form = EmployMonthlySalaryForm(instance=get_object_or_404(Monthly_Salaries, id=eid))
		return render(request, 'expenses/EditEmployMonthlySalaryForm.html', {'form': form, 'pdata':pdata})

@login_required
def Get_Order_Wise_Salaries(request, proj, month, mode):
	pdata = projectname(request, proj)
	dt = date.today()
	sal = None

	url = '/'+str(pdata['pj'])+'/monthlysalaries/month/select/'

	if month != 'month':
		try:
			month = datetime.strptime(month, '%Y-%m')
			mnth = datetime.strftime(month, '%Y-%m')
			m = month.month
		except:
			messages.error(request, 'Please Select Proper Month Format')
			return render(request, 'expenses/OrderWiseSalaries.html', {'month': 'month', 'pdata':pdata, 'mode':'select'})

		if month.year > dt.year or (month.year == dt.year and month.month > dt.month ) :
	 		messages.error(request, 'Current Month Not Completed to Generate Order Wise Salaries')
	 		return render(request, 'expenses/OrderWiseSalaries.html', {'month': 'month', 'pdata':pdata, 'mode':'select'})

	if mode == 'select':
		return render(request, 'expenses/OrderWiseSalaries.html', {'month': 'month', 'pdata':pdata, 'mode':'select'})
	
	m_atnd = Monthatnd.objects.filter(Month__month=m, Month__year=month.year)
	sal = Monthly_Salaries.objects.filter(Month__month=m, Month__year=month.year)
	empls = Account.objects.filter(Status=1, ds=1).order_by('Sr_No')
	k = working_days(request, month)
	if month.year == dt.year and m == dt.month:
		mnth = m
		n, num = 0, 0
		while mnth == m:
			n = n + 1
			ndt = dt + timedelta(days=n)
			if date.today().strftime('%a') != 'Sun':
				num = num + 1
			mnth = ndt.month
		k = k + num

	if not sal and mode == 'get':
		messages.error(request, 'Salaries Not Yet Generated for the Selected Month')
		return render(request, 'expenses/OrderWiseSalaries.html', {'month': 'month', 'pdata':pdata, 'mode':'select'})

	orders_list = []
	sal_list = []
	if sal:
		atnd = Attendance.objects.filter(Date__month=m, Date__year=month.year, Sales_Order__isnull=False)
		if atnd:
			for x in atnd:
				orders_list.append(x.Sales_Order)
			orders_list = list(dict.fromkeys(orders_list))
		for order in orders_list:
			t_sal = 0
			for e in empls:
				a1 = atnd.filter(Q(Name=e, Sales_Order=order, Day_Status='Present')|Q(Day_Status='On Duty')|Q(Day_Status='Tour'))
				a2 = atnd.filter(Name=e, Sales_Order=order, Day_Status='Half Day')
				t_presents = len(a1) + (len(a2)/2)
				sal = Empl_Salaries.objects.filter(Employ_Name=e).last()	
				if sal:
					d_sal = sal.Gross_Salary/k
					t_sal = t_sal + t_presents*d_sal
			sal_list.append(t_sal)
	data = zip(orders_list, sal_list)

	total = sum(sal_list) or 0

	return render(request, 'expenses/OrderWiseSalaries.html', {'month': mnth, 'month1':month, 'pdata':pdata, 'data':data,  'mode':'get', 'total':total})


@login_required
def Employ_Claims(request, proj):
	pdata = projectname(request, proj)
	lookup = {'Related_Project__isnull':False}
	expns = Expenses.objects.filter(Q(Submitted_By__Status=1)&Q(Submitted_By__ds=1)&Q(Approval_Status=1))
	debits = Debit_Amounts.objects.filter(Employ__isnull=False)
	debits = debits.filter(Q(Employ__Status=1)&Q(Employ__ds=1))
	empls = []
	for e in expns:
		empls.append(e.Submitted_By)
	for e in debits:
		empls.append(e.Employ)

	empls = list(dict.fromkeys(empls))

	employs, total_claims, paid, due, advances, sal_advances = [], [], [], [], [], []

	for e in empls:
		employs.append(e)
		dbt_sum, dbt_sum1, d, exp_issue = 0,0,0,0
		exp = Expenses.objects.filter(Submitted_By=e, Approval_Status=1)
		dbt = Debit_Amounts.objects.filter(Employ=e)
		dbt1 = dbt.filter(Related_To='Salary Advance')
		t_claims = sum(exp.values_list('Total_Amount', flat=True)) if exp != None else 0
		dbt_sum = sum(dbt.values_list('Issued_Amount', flat=True)) if dbt != None else 0
		dbt1_sum = sum(dbt1.values_list('Issued_Amount', flat=True)) if dbt1 != None else 0
		exp_issue = dbt_sum - dbt1_sum
		d = t_claims - exp_issue
		due.append((t_claims - exp_issue) if (t_claims - exp_issue) > 0 else 0)
		advances.append(-(d)) if d < 0 else advances.append(0)
		sal_advances.append(dbt1_sum)
		paid.append(exp_issue)
		total_claims.append(t_claims)

	data = zip(employs, total_claims, paid, due, advances, sal_advances)
	return render(request, 'expenses/EmployWiseClaims.html', {'pdata':pdata, 'data':data})

@login_required
def Month_Attendance_Edit(request, proj, empl, dt, fnc):
	pdata = projectname(request, proj)
	month = datetime.strptime(dt, '%Y-%m-%d')
	month = month.strftime('%Y-%m')
	atnd = Attendance.objects.filter(Name__id=empl, Date=dt).last()
	acnt = Account.objects.get(id=empl)
	if atnd:
		eid = atnd.id
	
	if fnc == 'edit':
		if request.method == 'POST':
			form = AttendanceForm1(request.POST, instance=get_object_or_404(Attendance, id=eid))
			if form.is_valid():
				p= form.save()
				p.Is_Manual = True
				p.save()
				if p.Day_Status == 'Absent' or p.Day_Status == 'Leave':
					p.Start_Time, p.End_Time, p.Total_Hours = None, None, None
					p.save()
					update_month_atnd(request, p.id)
				if p.End_Time:
					update_month_atnd(request, p.id)
				messages.success(request, "Attendance for the Selected Emoploy Has Been Updated Successfully")
				url = '/'+str(pdata['pj'])+'/monthwiseattendancelist/'+month+'/'
				return redirect(url)
			else:
				messages.error(request, get_errors(request, form.errors))
				url = '/'+str(pdata['pj'])+'/monthwiseattendancelist/'+month+'/'
				return redirect(url)
		else:
			form = AttendanceForm(instance=get_object_or_404(Attendance, id=eid))
			form.fields["Sales_Order"].queryset = Orders.objects.filter(Final_Status=0) 
			return render(request, 'attendance/AttendanceForm1.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
	# elif fnc == 'delete':
	# 	atnd = Attendance.objects.get(id=eid)
	# 	dt = atnd.Date
	# 	empl = atnd.Name
	# 	atnd.delete()
	# 	atnd = Attendance.objects.filter(Name=empl).order_by('Date').last()
	# 	update_month_atnd(request, atnd.id) if atnd != None else None
	# 	messages.success(request, "Attendance for the Selected Emoploy Has Been Deleted")
	# 	if returnpage == 'employwise':
	# 		dt = str(dt.strftime('%Y-%m'))
	# 		url = '/'+str(pdata['pj'])+'/employwiseattendance/'+dt+'/'+empl.Name+'/'
	# 	else:
	# 		url = '/'+str(pdata['pj'])+'/daywiseattendancelist/day/'
	# 	return redirect(url)
	else:
		if request.method == 'POST':
			form = AttendanceForm(request.POST)
			data_copy = request.POST.items()
			if form.is_valid():
				p= form.save(commit=False)
				atnd = Attendance.objects.filter(Date=p.Date)
				if atnd:
					for x in atnd: 
						if p.Name == x.Name:
							messages.error(request, "Employ Attendance Already Registered, Please Check Employ Name Again")
							form = AttendanceForm(initial=data_copy)
							return render(request, 'attendance/AttendanceForm1.html', {'form': form, 'pdata':pdata, 'fnc':fnc})

				p.Issued_By = Account.objects.get(user=request.user)
				
				if p.Day_Status == 'Absent' or p.Day_Status == 'Leave':
					p.Start_Time, p.End_Time, p.Total_Hours = None, None, None
					p.save()
					update_month_atnd(request, p.id)
				p.Is_Manual = True
				p.save()
				if p.End_Time:
					update_month_atnd(request, p.id)
				
				messages.success(request, "Attendance for the Selected Emoploy Has Been Added Successfully")
				url = '/'+str(pdata['pj'])+'/monthwiseattendancelist/'+month+'/'
				return redirect(url)
			else:				
				return render(request, 'attendance/AttendanceForm1.html', {'form': form, 'pdata':pdata, 'fnc':fnc})
		else:
			form = AttendanceForm(initial={'Date':dt, 'Name':acnt, 'Day_Status':None})
			form.fields["Sales_Order"].queryset = Orders.objects.filter(Final_Status=0, Related_Project__Short_Name='Services') 
			return render(request, 'attendance/AttendanceForm1.html', {'form': form, 'pdata':pdata, 'fnc':fnc})


