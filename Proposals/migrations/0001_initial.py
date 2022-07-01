# Generated by Django 3.2.8 on 2022-05-24 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('UserAccounts', '0014_alter_account_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=40, null=True)),
                ('Address_Line_1', models.CharField(blank=True, help_text='Address Line 1', max_length=40, null=True)),
                ('Address_Line_2', models.CharField(blank=True, help_text='Address Line 2', max_length=35, null=True)),
                ('State', models.CharField(choices=[('Telangana', 'Telangana'), ('AP', 'AP')], max_length=20, null=True)),
                ('GST_No', models.CharField(blank=True, help_text='Provide If Company under GST', max_length=15, null=True)),
                ('Phone_Number_1', models.CharField(help_text='10 Digit Main Phone Number', max_length=10, null=True)),
                ('Phone_Number_2', models.CharField(blank=True, help_text='Optional Phone Number', max_length=10, null=True)),
                ('Email', models.EmailField(help_text='Company Contact Mail Address', max_length=40, null=True)),
                ('Website', models.CharField(blank=True, max_length=40, null=True)),
                ('Office_Type', models.CharField(blank=True, choices=[('Registered', 'Registered'), ('Branch', 'Branch'), ('Manufacturing', 'Manufacturing'), ('Service', 'Service')], max_length=40, null=True)),
                ('Status', models.BooleanField(default=True, help_text='Unmark if Company Address not in Active')),
                ('ds', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='PowerCat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Capacity', models.IntegerField(help_text='Capacity in KW such as 1, 2, 3, 5, 7 KWp', null=True)),
                ('No_of_Panels', models.IntegerField(help_text='Number of Solar Panels', null=True)),
                ('Panel_Capacity', models.IntegerField(help_text='Each Panel Capacity in Watts such as 300, 350', null=True)),
                ('Module_Type', models.CharField(choices=[('Poly Crystalline', 'Poly Crystalline'), ('Mono Crystalline', 'Mono Crystalline'), ('Mono Perk', 'Mono Perk')], max_length=50, null=True)),
                ('Cells_Type', models.CharField(choices=[('DCR', 'DCR'), ('Non-DCR', 'Non-DCR')], max_length=30, null=True)),
                ('Phase_Configuration', models.CharField(choices=[('3-Phase', '3-Phase'), ('Single Phase', 'Single Phase')], max_length=30, null=True)),
                ('Ref_No', models.CharField(blank=True, max_length=30, null=True)),
                ('Revision_Date', models.DateField(blank=True, null=True)),
                ('Status', models.BooleanField(default=True, help_text='Unmark if it is not in Active')),
                ('ds', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(help_text='Name of The Customer', max_length=40, null=True)),
                ('Phone_Number', models.CharField(help_text='10 Digit Main Phone Number', max_length=10, null=True)),
                ('Power_Bill', models.CharField(blank=True, choices=[('Less than 1000', 'Less than 1000'), ('1000 to 3000', '1000 to 3000'), ('3000 to 6000', '3000 to 6000'), ('Above 6000', 'Above 6000')], max_length=30, null=True)),
                ('Address_Line_1', models.CharField(blank=True, help_text='Address Line 1', max_length=40, null=True)),
                ('Address_Line_2', models.CharField(blank=True, help_text='Address Line 2', max_length=40, null=True)),
                ('State', models.CharField(blank=True, choices=[('Telangana', 'Telangana'), ('AP', 'AP')], help_text='Choose Your State', max_length=40, null=True)),
                ('Email', models.EmailField(blank=True, help_text='Email Address If You Have', max_length=28, null=True)),
                ('Solar_Panels_Make', models.CharField(blank=True, help_text='Specify if You Need any Specific Make', max_length=40, null=True)),
                ('Inverter_Make', models.CharField(blank=True, help_text='Specify if You Need any Specific Make', max_length=40, null=True)),
                ('Inverter_Capacity', models.IntegerField(blank=True, help_text='Capacity in KW such as 1, 2, 3, 5, 7 KW', null=True)),
                ('Message', models.TextField(blank=True, help_text='Message If Anything Specific To Discuss or Request', max_length=500, null=True)),
                ('Proposal_No_1', models.IntegerField(blank=True, null=True, unique=True)),
                ('Proposal_No', models.CharField(blank=True, max_length=30, null=True, unique=True)),
                ('Date', models.DateTimeField(blank=True, null=True)),
                ('Is_Gen', models.BooleanField(default=False)),
                ('Type', models.CharField(blank=True, choices=[('Residential', 'Residential'), ('Commercial', 'Commercial'), ('Industrial', 'Industrial')], help_text='Choose Wether it Resedential or Commercial', max_length=40, null=True)),
                ('Capacity', models.ForeignKey(blank=True, help_text='Choose Your Required Capacity in KW', null=True, on_delete=django.db.models.deletion.CASCADE, to='Proposals.powercat')),
            ],
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Proposal_No_1', models.IntegerField(blank=True, null=True, unique=True)),
                ('Tender_Cost', models.FloatField(help_text='Tender Cost As Per Govt. in INR', max_length=10, null=True)),
                ('Supplier_Add_On_Cost', models.FloatField(help_text='Supplier Add On Cost in INR', max_length=10, null=True)),
                ('DD1_Charges', models.FloatField(help_text='DD Charges Against Power Distribution Dept. for Net Metering', max_length=7, null=True)),
                ('DD2_Charges', models.FloatField(help_text='DD Against Nodel Agency Ex: TSSPDCL, APSPDCL..', max_length=7, null=True)),
                ('High_Raised_Structure', models.FloatField(help_text='Cost of High Raised Structure Extra', max_length=7, null=True)),
                ('Subsidy', models.FloatField(help_text='Subsidy Part', max_length=7, null=True)),
                ('Cables', models.FloatField(blank=True, default=0, help_text='Cable Charges', max_length=7, null=True)),
                ('Type', models.CharField(blank=True, help_text='Choose Wether it Resedential or Commercial', max_length=40, null=True)),
                ('GST_Amount', models.FloatField(blank=True, help_text='Add GST % if it is commercial, such as 12, 18, 28 etc', max_length=5, null=True)),
                ('Cost_To_Client', models.FloatField(blank=True, help_text='Cost to Client', max_length=10, null=True)),
                ('Additional_Cost', models.CharField(blank=True, help_text='Example: ₹ 15,000 **Some Transport Cost Included', max_length=40, null=True)),
                ('Date', models.DateTimeField(blank=True, null=True)),
                ('Status', models.BooleanField(default=False, help_text='Tick if Order Confirmed and Received PO')),
                ('Rivision', models.IntegerField(blank=True, null=True)),
                ('Account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='UserAccounts.account')),
                ('From_Company', models.ForeignKey(help_text='Quoted Company Address', null=True, on_delete=django.db.models.deletion.CASCADE, to='Proposals.companydetails')),
                ('Proposal_To', models.ForeignKey(help_text='Proposal Details', null=True, on_delete=django.db.models.deletion.CASCADE, to='Proposals.proposal', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Costing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nodel_Agency', models.CharField(choices=[('TSREDCO', 'TSREDCO'), ('NREDCAP', 'NREDCAP'), ('CREDA', 'CREDA')], max_length=30, null=True)),
                ('Tender_Cost', models.FloatField(help_text='Tender Cost As Per Govt. in INR', max_length=10, null=True)),
                ('Supplier_Add_On_Cost', models.FloatField(help_text='Supplier Add On Cost in INR', max_length=10, null=True)),
                ('DD1_Charges', models.FloatField(help_text='DD Charges Against Power Distribution Dept. for Net Metering', max_length=7, null=True)),
                ('DD2_Charges', models.FloatField(help_text='DD Against Nodel Agency Ex: TSREDCO, NREDCAP..', max_length=7, null=True)),
                ('High_Raised_Structure', models.FloatField(help_text='Cost of High Raised Structure Extra', max_length=7, null=True)),
                ('Subsidy', models.FloatField(help_text='Subsidy Amount Provided By Govt.', max_length=7, null=True)),
                ('Cables', models.FloatField(blank=True, default=0, help_text='Cable Charges', max_length=7, null=True)),
                ('Ref_No', models.CharField(blank=True, max_length=30, null=True)),
                ('Revision_Date', models.DateField(blank=True, null=True)),
                ('ds', models.BooleanField(default=True)),
                ('Capacity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Proposals.powercat', unique=True)),
            ],
        ),
    ]
