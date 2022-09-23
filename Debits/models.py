from django.db import models
from Orders.models import Orders
from Projects.models import Projects, CompanyDetails
from UserAccounts.models import Account, Empl_Salaries

maincat 			= (('Services', 'Services'), ('Supplies', 'Supplies'), ('Factory', 'Factory'), ('Marketing', 'Marketing'), ('Office', 'Office'), ('Dispatches', 'Dispatches'), ('Others', 'Others'))
maincat1 			= (('Services', 'Services'), ('Marketing', 'Marketing'), ('Office', 'Office'), ('Salary Advance', 'Salary Advance'), ('Dispatches', 'Dispatches'), ('Others', 'Others'))
against				= ( ('Travel', 'Travel'), ('Food', 'Food'), ('Lodging', 'Lodging'), ('Fuel', 'Fuel'), ('Repair', 'Repair'), ('Transportation', 'Transportation'), ('Recharges', 'Recharges'), ('Stationery', 'Stationery'), ('General Purchase', 'General Purchase'), ('Miscellaneous', 'Miscellaneous'))

class Expenses(models.Model):
	Related_Project		= models.ForeignKey(Projects, null=True, blank=True, on_delete=models.SET_NULL)
	Related_Company		= models.ForeignKey(CompanyDetails, null=True, blank=True, on_delete=models.SET_NULL) 	
	Reference_No		= models.CharField(max_length=20, null=True, blank=True, unique=True, help_text='voucher no')
	Ref_No				= models.IntegerField(null=True, blank=True) 
	FY					= models.CharField(max_length=6, null=True, blank=True) 
	Submitted_By		= models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name='submittedby') 
	Approval_Request_To	= models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name='approvedby')
	From_Date 			= models.DateField(null=True, blank=True, help_text='start date')
	To_Date 			= models.DateField(null=True, blank=True, help_text='end date')
	Related_To 			= models.CharField(max_length=30, choices=maincat, null=True)
	Sales_Order			= models.ForeignKey(Orders, null=True, blank=True, on_delete=models.SET_NULL)
	Purpose	    		= models.CharField(max_length=100, null=True, help_text='purpose of expenses')
	Total_Amount		= models.FloatField(max_length=10, null=True, blank=True, help_text='amount in rupees')
	Balance_Amount		= models.FloatField(max_length=10, null=True, blank=True, help_text='due amount')
	Lock_Status 		= models.BooleanField(default=False, help_text='lock status')	
	Approval_Status 	= models.BooleanField(default=False, help_text='approval status')	
	Issued_By			= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='issueddby')
	Remarks	    		= models.TextField(max_length=500, null=True, blank=True, help_text='specify if any other things to describe')
	Submitted_Date 		= models.DateField(null=True, blank=True, help_text='date of submission')
	Issued_Date 		= models.DateField(null=True, blank=True, help_text='date of amount issued')
	Over_Due_Days 		= models.IntegerField(null=True, blank=True)
	Clearing_Status 	= models.BooleanField(default=False, help_text='mark if all amounts cleared')
	Edit_Status 		= models.BooleanField(default=False, help_text='mark if want to lock edit')	
	Balance_Advance		= models.FloatField(default=0, max_length=10, null=True, blank=True, help_text='if any advance at that time')
	

	def __str__(self):
		return str(self.Reference_No)+'/'+str(self.Submitted_By)+'/'+str(self.Total_Amount)

class Exp_Items(models.Model):
	Expenses			= models.ForeignKey(Expenses, null=True, blank=True, on_delete=models.CASCADE) 	
	From_Date 			= models.DateField(null=True, help_text='start date or date of expense')
	To_Date 			= models.DateField(null=True, blank=True, help_text='end date')
	Category 			= models.CharField(max_length=30, choices=against, null=True)
	Description  		= models.TextField(max_length=500, null=True, blank=True, help_text='such as petrol or bus/train/flight fares or vehicle charges or tools purchase or any other purchases etc..')
	Amount				= models.FloatField(max_length=10, null=True, help_text='amount in rupees')
	Attach				= models.FileField(upload_to='expenses/', null=True, blank=True, help_text='attch bill or related copy if available')

	def __str__(self):
		return str(self.Expenses.Reference_No)+'/'+str(self.From_Date)+'/'+str(self.Category)+'/Amount-'+str(self.Amount)

class Debit_Amounts(models.Model):
	paid_to = (('Against Expenses', 'Against Expenses'),('As Advance to Staff', 'As Advance to Staff'), ('Outside Party', 'Outside Party'))
	pay_type = (('Cash', 'Cash'),('Cheque','Cheque'),('UPI','UPI'), ('Account','Account'))
	Related_Project		= models.ForeignKey(Projects, null=True, blank=True, on_delete=models.SET_NULL)
	Related_Company		= models.ForeignKey(CompanyDetails, null=True, blank=True, on_delete=models.SET_NULL) 	
	Voucher_No			= models.IntegerField(null=True, blank=True, help_text='voucher no') 
	Employ				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='ifemploy') 
	Paid_To 			= models.CharField(max_length=30, choices=paid_to, null=True)
	Expenses			= models.ForeignKey(Expenses, null=True, blank=True, on_delete=models.SET_NULL) 	
	Issued_To			= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL) 
	Party_Name			= models.CharField(max_length=50, null=True, blank=True, help_text='outside party/company/person name') 
	Related_To 			= models.CharField(max_length=30, choices=maincat1, null=True, blank=True)
	Against 			= models.CharField(max_length=30, choices=against, null=True, blank=True)
	Amount_to_be_Pay	= models.FloatField(max_length=10, null=True, blank=True, help_text='amount to be pay or billed or claimed amount, if not entered it will take issued amount as billed amount')
	Issued_Amount		= models.FloatField(max_length=10, null=True, help_text='issued amount against billed/claimed amount')
	Issued_Date 		= models.DateField(null=True, blank=True, help_text='amount issued date')
	Payment_Mode 		= models.CharField(max_length=30, choices=pay_type, null=True)
	Cheque_Details 		= models.CharField(max_length=60, null=True, blank=True, help_text='cheque no and date if available, example 2358455221, 25-12-2022')
	Purpose	    		= models.TextField(max_length=500, null=True, blank=True, help_text='description of purpose/reason to issue amount')
	Approved_By			= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='amountapprovedby')
	Issued_By			= models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name='issuedamountby')
	As_Advance			= models.FloatField(max_length=10, null=True, help_text='balance remaining as advance')
	Attach				= models.FileField(upload_to='expenses/', null=True, blank=True, help_text='attch bill or related copy if available')
	Status 				= models.BooleanField(default=False, help_text='mark it if bill/expenses voucher cleared')	

	def __str__(self):
		return str(self.Voucher_No)+'-'+str(self.Issued_Date)+'-'+str(self.Issued_Amount)


class Staff_Advances(models.Model):
	Employ				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE, related_name='employee') 
	Advance				= models.FloatField(max_length=10, null=True, help_text='advances with employees')
	Issued_By			= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='advanceissueddby')
	Issued_Date 		= models.DateField(null=True, blank=True, help_text='date of amount issued')

	def __str__(self):
		return str(self.Employ)+'-'+str(self.Advance)

class Salary_Advances(models.Model):
	Employ				= models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE, related_name='employ1') 
	Advance				= models.FloatField(max_length=10, null=True, help_text='advances with employees')
	Issued_By			= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='advanceissueddby1')
	Issued_Date 		= models.DateField(null=True, blank=True, help_text='date of amount issued')

	def __str__(self):
		return str(self.Employ)+'-'+str(self.Advance)


class Attendance(models.Model):
	Name 				= models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='attender')
	Date                = models.DateField(null=True)
	Start_Time 			= models.TimeField(null=True, blank=True)
	End_Time 			= models.TimeField(null=True, blank=True) 
	Total_Hours 		= models.FloatField(max_length=5, null=True, blank=True)
	Day_Status 			= models.CharField(max_length=20, default='Present', null=True, blank=True, choices=(('Present', 'Present'), ('Absent', 'Absent'), ('Leave', 'Leave'), ('Half Day', 'Half Day'), ('Permission', 'Permission'), ('On Duty', 'On Duty'), ('Tour', 'Tour')))
	Sales_Order			= models.ForeignKey(Orders, null=True, blank=True, on_delete=models.SET_NULL)
	Issued_By			= models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='attendanceissuedby')
	Is_Manual           = models.BooleanField(default=True, help_text='generated maunaully or automatically')
	def __str__(self):
		return str(self.Name)+'-'+str(self.Date)+'-'+str(self.Start_Time)+'-'+str(self.End_Time)+'-'+str(self.Day_Status)

class Monthatnd(models.Model):
	Name 				= models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
	Month	 			= models.DateField(null=True, blank=True)	
	Presents 			= models.FloatField(max_length=4, null=True, blank=True)
	Leaves 				= models.FloatField(max_length=4, null=True, blank=True)
	Leaves_Left 		= models.FloatField(max_length=4, null=True, blank=True)
	Absents 			= models.FloatField(max_length=4, null=True, blank=True)
	Total_Hours 		= models.FloatField(max_length=5, null=True, blank=True)
	Total_OT 			= models.FloatField(max_length=5, null=True, blank=True)
	Last_Updated_Date	= models.DateField(null=True, blank=True)
	def __str__(self):
		return str(self.Name)+'-'+str(self.Presents)

class DeclareDayAs(models.Model):
	Date	 			= models.DateField(null=True, blank=True)
	Declare_Day_As 		= models.CharField(max_length=30, default='Holiday', null=True, choices=(('Holiday', 'Holiday'), ('Half Day', 'Half Day'), ('Working Day', 'Working Day')))
	Occassion 			= models.CharField(max_length=30, null=True, blank=True, help_text='reason for holiday/half day/workingday')
	Lock_Status 		= models.BooleanField(default=False)	

	def __str__(self):
		return str(self.Date)+'-'+str(self.Declare_Day_As)+'-'+str(self.Occassion)

class Working_Days(models.Model):
	Month	 			= models.DateField(null=True, blank=True)
	Working_Days 		= models.FloatField(max_length=4, null=True, blank=True)

	def __str__(self):
		return str(self.Month)+'-'+str(self.Working_Days)

class Monthly_Salaries(models.Model):
	Name 					= models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL)
	Month	 				= models.DateField(null=True, blank=True)	
	Issued_Salary 			= models.IntegerField(null=True, blank=True, help_text='issued salary or net salary for this month')
	Issued_Date 			= models.DateField(null=True, help_text='salary issued date')
	Presents 				= models.FloatField(max_length=5, null=True, blank=True)
	LOP 					= models.FloatField(max_length=10, null=True, blank=True, help_text='loss of pay if eligible')
	OT_Amount 				= models.IntegerField(null=True, blank=True, help_text='over time amount if eligible')
	PF						= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='PF employee share 12% of basic if eligible')
	ESI 					= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='3.25% employer on gross')
	Professional_Tax 		= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='PT deductions if eligible, <15K 0, 15-20K 150, >15K 200 of gross')
	TDS 					= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='TDS/income tax deductions if eligible')
	Other_Deductions 		= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='other deductions')
	Salary_Advance			= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='advances with employes')
	Issued_Status			= models.BooleanField(default=True, help_text='issued status')
	Automatic				= models.BooleanField(default=True)
	Last_Updated_Date	    = models.DateField(null=True, blank=True)

	def __str__(self):
		return str(self.Name.Name)+'-'+str(self.Issued_Date)+'-'+str(self.Issued_Salary)

class Month_Sal_Exp(models.Model):
	Month	 				= models.DateField(null=True, blank=True)	
	Issued_Salareis 		= models.IntegerField(null=True, blank=True, help_text='total issued salaries')
	Pending_Salaries 		= models.IntegerField(null=True, blank=True, help_text='pending salaries')
	Issued_Date 			= models.DateField(null=True, help_text='salary issued date')
	Total_LOP 				= models.FloatField(max_length=10, null=True, blank=True, help_text='loss of pay if eligible')
	Total_OT 				= models.IntegerField(null=True, blank=True, help_text='over time amount if eligible')
	Paid_PF					= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='PF employee share 12% of basic if eligible')
	Paid_ESI 				= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='3.25% employer on gross')
	Total_Paid 				= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='PT deductions if eligible, <15K 0, 15-20K 150, >15K 200 of gross')
	Total_TDS 				= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='TDS/income tax deductions if eligible')
	Other_Deductions 		= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='other deductions')
	Total_Advances			= models.FloatField(max_length=10, default=0, null=True, blank=True, help_text='advances with employes')
	Last_Updated_Date	    = models.DateField(null=True, blank=True)

	def __str__(self):
		return str(self.Month)+'-'+str(self.Issued_Date)+'-'+str(self.Issued_Salaries)