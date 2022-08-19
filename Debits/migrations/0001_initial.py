# Generated by Django 3.2.8 on 2022-07-27 23:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Projects', '0001_initial'),
        ('UserAccounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateField(null=True)),
                ('Start_Time', models.TimeField(null=True)),
                ('End_Time', models.TimeField(blank=True, null=True)),
                ('Total_Hours', models.FloatField(blank=True, max_length=5, null=True)),
                ('Day_Status', models.CharField(blank=True, choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Leave', 'Leave'), ('Half Day', 'Half Day'), ('Permission', 'Permission'), ('On Duty', 'On Duty'), ('Tour', 'Tour')], default='Present', max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Debit_Amounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Voucher_No', models.IntegerField(blank=True, help_text='voucher no', null=True)),
                ('Paid_To', models.CharField(choices=[('Against Expenses', 'Against Expenses'), ('As Advance to Staff', 'As Advance to Staff'), ('Outside Party', 'Outside Party')], max_length=30, null=True)),
                ('Party_Name', models.CharField(blank=True, help_text='outside party/company/person name', max_length=50, null=True)),
                ('Related_To', models.CharField(blank=True, choices=[('Services', 'Services'), ('Marketing', 'Marketing'), ('Office', 'Office'), ('Dispatches', 'Dispatches'), ('Others', 'Others')], max_length=30, null=True)),
                ('Against', models.CharField(blank=True, choices=[('Travel', 'Travel'), ('Food', 'Food'), ('Lodging', 'Lodging'), ('Fuel', 'Fuel'), ('Transportation', 'Transportation'), ('Recharges', 'Recharges'), ('Stationery', 'Stationery'), ('General Purchase', 'General Purchase'), ('Miscellaneous', 'Miscellaneous')], max_length=30, null=True)),
                ('Amount_to_be_Pay', models.FloatField(blank=True, help_text='amount to be pay or billed or claimed amount, if not entered it will take issued amount as billed amount', max_length=10, null=True)),
                ('Issued_Amount', models.FloatField(help_text='issued amount against billed/claimed amount', max_length=10, null=True)),
                ('Issued_Date', models.DateField(blank=True, help_text='amount issued date', null=True)),
                ('Payment_Mode', models.CharField(choices=[('Cash', 'Cash'), ('Cheque', 'Cheque'), ('UPI', 'UPI'), ('Account', 'Account')], max_length=30, null=True)),
                ('Cheque_Details', models.CharField(blank=True, help_text='cheque no and date if available, example 2358455221, 25-12-2022', max_length=60, null=True)),
                ('Purpose', models.TextField(blank=True, help_text='description of purpose/reason to issue amount', max_length=500, null=True)),
                ('As_Advance', models.FloatField(help_text='balance remaining as advance', max_length=10, null=True)),
                ('Attach', models.FileField(blank=True, help_text='attch bill or related copy if available', null=True, upload_to='expenses/')),
                ('Status', models.BooleanField(default=False, help_text='mark it if bill/expenses voucher cleared')),
            ],
        ),
        migrations.CreateModel(
            name='DeclareDayAs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateField(blank=True, null=True)),
                ('Declare_Day_As', models.CharField(choices=[('Holiday', 'Holiday'), ('Half Day', 'Half Day'), ('Working Day', 'Working Day')], default='Holiday', max_length=30, null=True)),
                ('Occassion', models.CharField(blank=True, help_text='reason for holiday/half day/workingday', max_length=30, null=True)),
                ('Lock_Status', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Exp_Items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('From_Date', models.DateField(help_text='start date or date of expense', null=True)),
                ('To_Date', models.DateField(blank=True, help_text='end date', null=True)),
                ('Category', models.CharField(choices=[('Travel', 'Travel'), ('Food', 'Food'), ('Lodging', 'Lodging'), ('Fuel', 'Fuel'), ('Transportation', 'Transportation'), ('Recharges', 'Recharges'), ('Stationery', 'Stationery'), ('General Purchase', 'General Purchase'), ('Miscellaneous', 'Miscellaneous')], max_length=30, null=True)),
                ('Description', models.TextField(blank=True, help_text='such as petrol or bus/train/flight fares or vehicle charges or tools purchase or any other purchases etc..', max_length=500, null=True)),
                ('Amount', models.FloatField(help_text='amount in rupees', max_length=10, null=True)),
                ('Attach', models.FileField(blank=True, help_text='attch bill or related copy if available', null=True, upload_to='expenses/')),
            ],
        ),
        migrations.CreateModel(
            name='Working_Days',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Month', models.DateField(blank=True, null=True)),
                ('Working_Days', models.FloatField(blank=True, max_length=4, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Staff_Advances',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Advance', models.FloatField(help_text='advances with employees', max_length=10, null=True)),
                ('Issued_Date', models.DateField(blank=True, help_text='date of amount issued', null=True)),
                ('Employ', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee', to='UserAccounts.account')),
                ('Issued_By', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='advanceissueddby', to='UserAccounts.account')),
            ],
        ),
        migrations.CreateModel(
            name='Monthatnd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Month', models.DateField(blank=True, null=True)),
                ('Presents', models.FloatField(blank=True, max_length=4, null=True)),
                ('Leaves', models.FloatField(blank=True, max_length=4, null=True)),
                ('Leaves_Left', models.FloatField(blank=True, max_length=4, null=True)),
                ('Absents', models.FloatField(blank=True, max_length=4, null=True)),
                ('Total_Hours', models.FloatField(blank=True, max_length=5, null=True)),
                ('Total_OT', models.FloatField(blank=True, max_length=5, null=True)),
                ('Last_Updated_Date', models.DateField(blank=True, null=True)),
                ('Name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='UserAccounts.account')),
            ],
        ),
        migrations.CreateModel(
            name='Expenses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Reference_No', models.CharField(blank=True, help_text='voucher no', max_length=20, null=True)),
                ('Ref_No', models.IntegerField(blank=True, null=True)),
                ('FY', models.CharField(blank=True, max_length=6, null=True)),
                ('From_Date', models.DateField(blank=True, help_text='start date', null=True)),
                ('To_Date', models.DateField(blank=True, help_text='end date', null=True)),
                ('Related_To', models.CharField(choices=[('Services', 'Services'), ('Marketing', 'Marketing'), ('Office', 'Office'), ('Dispatches', 'Dispatches'), ('Others', 'Others')], max_length=30, null=True)),
                ('Purpose', models.CharField(help_text='purpose of expenses', max_length=100, null=True)),
                ('Total_Amount', models.FloatField(blank=True, help_text='amount in rupees', max_length=10, null=True)),
                ('Balance_Amount', models.FloatField(blank=True, help_text='balance due/advance amount in rupees', max_length=10, null=True)),
                ('Lock_Status', models.BooleanField(default=False, help_text='lock status')),
                ('Approval_Status', models.BooleanField(default=False, help_text='approval status')),
                ('Remarks', models.TextField(blank=True, help_text='specify if any other things to describe', max_length=500, null=True)),
                ('Submitted_Date', models.DateField(blank=True, help_text='date of submission', null=True)),
                ('Issued_Date', models.DateField(blank=True, help_text='date of amount issued', null=True)),
                ('Over_Due_Days', models.IntegerField(blank=True, null=True)),
                ('Clearing_Status', models.BooleanField(default=False, help_text='mark if all amounts cleared')),
                ('Edit_Status', models.BooleanField(default=False, help_text='mark if want to lock edit')),
                ('Approval_Request_To', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approvedby', to='UserAccounts.account')),
                ('Issued_By', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issueddby', to='UserAccounts.account')),
                ('Related_Company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails')),
                ('Related_Project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.projects')),
            ],
        ),
    ]
