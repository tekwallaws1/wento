from django.db import models
from UserAccounts.models import *
from django.contrib.auth.models import User


states = (('Telangana','Telangana'), ('AP', 'AP'))

class CompanyDetails(models.Model):
	Name 					= models.CharField(max_length=40, null=True)
	Address_Line_1			= models.CharField(max_length=40, blank=True, null=True, help_text='Address Line 1')
	Address_Line_2			= models.CharField(max_length=35, blank=True, null=True, help_text='Address Line 2')
	State 					= models.CharField(max_length=20, null=True, choices=states)
	GST_No 					= models.CharField(max_length=15, blank=True, null=True, help_text='Provide If Company under GST')
	Phone_Number_1 			= models.CharField(max_length=10, null=True, help_text='10 Digit Main Phone Number')
	Phone_Number_2 			= models.CharField(max_length=10, null=True, blank=True, help_text='Optional Phone Number')
	Email 					= models.EmailField(max_length=40, null=True, help_text='Company Contact Mail Address')
	Website 				= models.CharField(max_length=40, blank=True, null=True)
	Office_Type				= models.CharField(max_length=40, blank=True, null=True, choices=(('Registered', 'Registered'), ('Branch', 'Branch'), ('Manufacturing', 'Manufacturing'), ('Service', 'Service')))
	Status 					= models.BooleanField(default = True, help_text='Unmark if Company Address not in Active')
	ds						= models.BooleanField(default=True)

	def __str__(self):
		return str(self.Name)+'-'+str(self.Address_Line_1)+'-'+str(self.Address_Line_2)+'-'+str(self.State)

class PowerCat(models.Model):
	Capacity 				= models.IntegerField(null=True, help_text='Capacity in KW such as 1, 2, 3, 5, 7 KWp')
	No_of_Panels 			= models.IntegerField(null=True, help_text='Number of Solar Panels')
	Panel_Capacity 			= models.IntegerField(null=True, help_text='Each Panel Capacity in Watts such as 300, 350')
	Module_Type 			= models.CharField(max_length=50, null=True, choices=(('Poly Crystalline', 'Poly Crystalline'), ('Mono Crystalline', 'Mono Crystalline'), ('Mono Perk', 'Mono Perk')))
	Cells_Type 				= models.CharField(max_length=30, null=True, choices=(('DCR', 'DCR'), ('Non-DCR', 'Non-DCR')))
	Phase_Configuration		= models.CharField(max_length=30, null=True, choices=(('3-Phase', '3-Phase'), ('Single Phase', 'Single Phase')))
	Ref_No					= models.CharField(max_length=30, null=True, blank=True) #Automatically Generated
	Revision_Date			= models.DateField(null=True, blank=True) #Automatically Generated
	Status 					= models.BooleanField(default = True, help_text='Unmark if it is not in Active')
	ds						= models.BooleanField(default=True)

	def __str__(self):
		return str(self.Capacity)+'KWp'+'-'+str(self.Phase_Configuration)+'-'+str(self.Panel_Capacity)+'Wp'+'-'+str(self.Module_Type)+'-'+str(self.Cells_Type)

class Costing(models.Model): 
	Capacity 				= models.ForeignKey(PowerCat, unique=True, on_delete=models.CASCADE, null=True)
	Nodel_Agency			= models.CharField(max_length=30, null=True, choices=(('TSREDCO', 'TSREDCO'), ('NREDCAP', 'NREDCAP'), ('CREDA', 'CREDA')))
	Tender_Cost	 			= models.FloatField(max_length=10, null=True, help_text='Tender Cost As Per Govt. in INR')
	Supplier_Add_On_Cost	= models.FloatField(max_length=10, null=True, help_text='Supplier Add On Cost in INR')
	DD1_Charges 			= models.FloatField(max_length=7, null=True, help_text='DD Charges Against Power Distribution Dept. for Net Metering')
	DD2_Charges 			= models.FloatField(max_length=7, null=True, help_text='DD Against Nodel Agency Ex: TSREDCO, NREDCAP..')
	High_Raised_Structure	= models.FloatField(max_length=7, null=True, help_text='Cost of High Raised Structure Extra')
	Subsidy					= models.FloatField(max_length=7, null=True, help_text='Subsidy Amount Provided By Govt.')
	Cables					= models.FloatField(default=0, max_length=7, null=True, blank=True, help_text='Cable Charges')
	Ref_No					= models.CharField(max_length=30, null=True, blank=True) #Automatically Generated
	Revision_Date			= models.DateField(null=True, blank=True) #Automatically Generated
	ds						= models.BooleanField(default=True)

	def __str__(self):
		return str(self.Tender_Cost)+'-'+str(self.Capacity)
 
class Proposal(models.Model):
	Name					= models.CharField(max_length=40, null=True, help_text='Name of The Customer')
	Phone_Number 			= models.CharField(max_length=10, null=True, help_text='10 Digit Main Phone Number')
	Capacity 				= models.ForeignKey(PowerCat, on_delete=models.CASCADE, blank=True, null=True, help_text='Choose Your Required Capacity in KW')
	Power_Bill				= models.CharField(max_length=30, null=True, blank=True, choices=(('Less than 1000', 'Less than 1000'), ('1000 to 3000', '1000 to 3000'), ('3000 to 6000', '3000 to 6000'), ('Above 6000', 'Above 6000')))

	Address_Line_1			= models.CharField(blank=True, max_length=40, null=True, help_text='Address Line 1')
	Address_Line_2			= models.CharField(blank=True, max_length=40, null=True, help_text='Address Line 2')
	State					= models.CharField(blank=True, max_length=40, null=True, choices=states, help_text='Choose Your State')
	Email					= models.EmailField(blank=True, max_length=28, null=True, help_text='Email Address If You Have')
	
	Solar_Panels_Make		= models.CharField(blank=True, max_length=40, null=True, help_text='Specify if You Need any Specific Make')
	Inverter_Make			= models.CharField(blank=True, max_length=40, null=True, help_text='Specify if You Need any Specific Make')
	Inverter_Capacity 		= models.IntegerField(null=True, blank=True, help_text='Capacity in KW such as 1, 2, 3, 5, 7 KW')
	Message					= models.TextField(max_length=500, blank=True, null=True, help_text='Message If Anything Specific To Discuss or Request')
	
	Proposal_No_1			= models.IntegerField(null=True, blank=True, unique=True) #Automatically Generated Only Number
	Proposal_No				= models.CharField(max_length=30, null=True, blank=True, unique=True) #Automatically Generated Total Proposal No
	Date					= models.DateTimeField(null=True, blank=True) #Automatically Generated
	Is_Gen 					= models.BooleanField(default = False) #backend if quote generated hide generate button
	Type 					= models.CharField(blank=True, max_length=40, null=True, choices=(('Residential', 'Residential'), ('Commercial', 'Commercial'), ('Industrial', 'Industrial')), help_text='Choose Wether it Resedential or Commercial')

	def __str__(self):
		return str(self.Name)+'-'+str(self.Phone_Number)+'-'+str(self.Capacity)

class Quote(models.Model):
	Account 				= models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)#backend
	From_Company 			= models.ForeignKey(CompanyDetails, on_delete=models.CASCADE, null=True, help_text='Quoted Company Address')
	Proposal_To 			= models.ForeignKey(Proposal, on_delete=models.CASCADE, unique=True, null=True, help_text='Proposal Details')
	Proposal_No_1			= models.IntegerField(null=True, blank=True, unique=True) #Automatically Generated Only Number

	Tender_Cost	 			= models.FloatField(max_length=10, null=True, help_text='Tender Cost As Per Govt. in INR')
	Supplier_Add_On_Cost	= models.FloatField(max_length=10, null=True, help_text='Supplier Add On Cost in INR')
	DD1_Charges 			= models.FloatField(max_length=7, null=True, help_text='DD Charges Against Power Distribution Dept. for Net Metering')
	DD2_Charges 			= models.FloatField(max_length=7, null=True, help_text='DD Against Nodel Agency Ex: TSSPDCL, APSPDCL..')
	High_Raised_Structure	= models.FloatField(max_length=7, null=True, help_text='Cost of High Raised Structure Extra')
	Subsidy					= models.FloatField(max_length=7, null=True, help_text='Subsidy Part')
	Cables					= models.FloatField(default=0, max_length=7, null=True, blank=True, help_text='Cable Charges')

	Type 					= models.CharField(blank=True, max_length=40, null=True, help_text='Choose Wether it Resedential or Commercial')
	GST_Amount 				= models.FloatField(max_length=5, null=True, blank=True, help_text='Add GST % if it is commercial, such as 12, 18, 28 etc') #Automatically Generated
	Cost_To_Client	 		= models.FloatField(max_length=10, null=True, blank=True, help_text='Cost to Client')
	# Additional_Cost			= models.CharField(blank=True, max_length=40, null=True, help_text='Example: ₹ 15,000 **Some Transport Cost Included')

	Date					= models.DateTimeField(null=True, blank=True) #Automatically Generated
	Status 					= models.BooleanField(default = False, help_text='Tick if Order Confirmed and Received PO')
	Rivision				= models.IntegerField(null=True, blank=True) #Automatically Generated Only Number

	def __str__(self):
		return str(self.Proposal_No_1)+'-'+str(self.Tender_Cost)