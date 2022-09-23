# Generated by Django 3.2.8 on 2022-09-19 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Projects', '0001_initial'),
        ('UserAccounts', '0015_empl_salaries_effective_from'),
    ]

    operations = [
        migrations.CreateModel(
            name='Billed_Items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Quantity', models.FloatField(max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BillRefNo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Bill_No_1', models.IntegerField(blank=True, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Copy_Billed_Items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Item_Description', models.TextField(blank=True, help_text='Item description', max_length=1000, null=True)),
                ('Item_Code', models.CharField(blank=True, help_text='Item Code', max_length=15, null=True)),
                ('HSN_Code', models.IntegerField(blank=True, help_text='HSN/SAC Code for this product', null=True)),
                ('Quantity', models.FloatField(help_text='quantity', max_length=10, null=True)),
                ('UOM', models.CharField(choices=[('No', 'No'), ('Set', 'Set'), ('Kg', 'Kg'), ('Mtr', 'Mtr'), ('Ltr', 'Ltr'), ('Bag', 'Bag')], max_length=15, null=True)),
                ('Unit_Price', models.FloatField(blank=True, help_text='each unit price excluding all taxes', max_length=15, null=True)),
                ('GST', models.FloatField(blank=True, help_text='GST in % such as 12, 18 etc', max_length=5, null=True)),
                ('CESS', models.FloatField(blank=True, help_text='CESS in % if applicable', max_length=5, null=True)),
                ('Other_Taxes', models.FloatField(blank=True, help_text='specify if any other taxes in % only', max_length=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Delivery_Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date', models.DateField(blank=True, help_text='date of dispatch', null=True)),
                ('Transport_Mode', models.CharField(blank=True, choices=[('By Road', 'By Road'), ('By Air', 'By Air')], max_length=20, null=True)),
                ('LUT_No', models.CharField(blank=True, help_text='lut no', max_length=30, null=True)),
                ('Vehicle_No', models.CharField(blank=True, help_text='vehicle number', max_length=20, null=True)),
                ('Vehicle_Type', models.CharField(blank=True, help_text='truck, bus, train, car etc..', max_length=20, null=True)),
                ('Place_Of_Supply', models.CharField(blank=True, help_text='place of supply', max_length=30, null=True)),
                ('LRR_No', models.CharField(blank=True, help_text='specify if any', max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Inv_Adjust_Table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Table_No', models.IntegerField(blank=True, null=True)),
                ('Row_No', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Invoices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Invoice_No', models.CharField(blank=True, help_text='invoice/bill no', max_length=30, null=True)),
                ('Invoice_No_1', models.IntegerField(blank=True, default=0, null=True)),
                ('FY', models.CharField(blank=True, help_text='financial year such as 22-23, 23-24 etc..', max_length=10, null=True)),
                ('Invoice_Date', models.DateTimeField(blank=True, help_text='billed date', null=True)),
                ('Invoice_Amount', models.FloatField(blank=True, default=0, help_text='including all taxes', max_length=20, null=True)),
                ('GST_Amount', models.FloatField(blank=True, help_text='only GST Amount', max_length=10, null=True)),
                ('CESS_Amount', models.FloatField(blank=True, help_text='CESS Amount', max_length=10, null=True)),
                ('GST_Reverse_Charges', models.BooleanField(default=False, help_text='default nill, if applicable mark it')),
                ('Credit_Days', models.IntegerField(blank=True, default=0, help_text='credit in days such as 0, 15, 30, 60 etc..', null=True)),
                ('Payment_Terms', models.CharField(blank=True, help_text='payment terms', max_length=100, null=True)),
                ('Payment_Over_Due_Days', models.IntegerField(blank=True, help_text='overdue in days such as 0, 30 etc..', null=True)),
                ('Payment_Due_Date', models.DateField(blank=True, help_text='payment due date', null=True)),
                ('Due_Amount', models.FloatField(blank=True, help_text='Due amount till date against billed', max_length=20, null=True)),
                ('Final_Payment_Status', models.BooleanField(default=False, help_text='Final Payment Status')),
                ('Payment_Cleared_Date', models.DateTimeField(blank=True, help_text='date of payment clearing', null=True)),
                ('Remarks', models.TextField(blank=True, max_length=500, null=True)),
                ('Lock_Status', models.BooleanField(default=False, help_text='mark if wnat to lock invoice to avoid editing')),
                ('Is_Proforma', models.BooleanField(default=False, help_text='tick if it is proforma invoice')),
                ('Attach', models.FileField(blank=True, help_text='attach invoice copy if available', null=True, upload_to='customerinvoices/')),
                ('Is_Manual', models.BooleanField(default=False, help_text='wether it is manual entry or online generation')),
                ('Set_For_Returns', models.BooleanField(default=True)),
                ('Amended_GST_Returns_Date', models.DateField(blank=True, help_text='any date in a month which you want make returns', null=True)),
                ('ds', models.BooleanField(default=True)),
                ('Last_Update', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order_Items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Quantity', models.FloatField(help_text='no of items', max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderRefNo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Order_No_1', models.IntegerField(blank=True, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Order_Details', models.TextField(blank=True, help_text='overall order short description', max_length=1000, null=True)),
                ('Order_No', models.CharField(blank=True, help_text='internal purpose - order reference number', max_length=30, null=True, unique=True)),
                ('Order_No_1', models.IntegerField(blank=True, default=0, null=True)),
                ('FY', models.CharField(blank=True, help_text='financial year such as 22-23, 23-24 etc..', max_length=10, null=True)),
                ('Order_Value', models.FloatField(blank=True, help_text='order value or estimated value', max_length=20, null=True)),
                ('Order_Type', models.CharField(choices=[('Confirmed', 'Confirmed'), ('Pipeline', 'Pipeline')], max_length=20, null=True)),
                ('Order_Received_Date', models.DateTimeField(blank=True, help_text='received order date', null=True)),
                ('Order_Through', models.CharField(choices=[('By PO', 'By PO'), ('By Mail', 'By Mail'), ('By Phone', 'By Phone'), ('By Reference', 'By Reference')], max_length=20, null=True)),
                ('Final_Status', models.BooleanField(default=False, help_text='Total Works and Payments Status')),
                ('PO_No', models.CharField(blank=True, help_text='Purchase Order Number if available', max_length=30, null=True)),
                ('PO_Status', models.BooleanField(default=False, help_text='PO work completion status, mark if PO work completed')),
                ('Can_Gen_Invoice', models.BooleanField(default=True, help_text='False if PO amount less than all onvoices amount')),
                ('Is_Billed', models.BooleanField(default=False)),
                ('Attach', models.FileField(blank=True, help_text='attach PO copy if available', null=True, upload_to='orders/')),
                ('ds', models.BooleanField(default=True)),
                ('Billing_Status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Orders.invoices')),
                ('Customer_Name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.custdt')),
                ('Order_Reference_Person', models.ForeignKey(blank=True, help_text='order reference person name', null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.custcontdt')),
            ],
        ),
        migrations.CreateModel(
            name='Sales_TC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Terms_and_Condition1', models.CharField(blank=True, help_text='optional', max_length=70, null=True)),
                ('Terms_and_Condition2', models.CharField(blank=True, help_text='optional', max_length=70, null=True)),
                ('Terms_and_Condition3', models.CharField(blank=True, help_text='optional', max_length=70, null=True)),
                ('Terms_and_Condition4', models.CharField(blank=True, help_text='optional', max_length=70, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Work_Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Current_Status', models.TextField(help_text='current progress/status', max_length=100, null=True)),
                ('Date', models.DateTimeField(blank=True, help_text='status update date', null=True)),
                ('Next_Task', models.TextField(blank=True, help_text='next work/stage details want to do', max_length=100, null=True)),
                ('Target_Date', models.DateTimeField(blank=True, help_text='schedule/target date for next work', null=True)),
                ('Closing_Status', models.BooleanField(default=False, help_text='tick if product delivered and excecuted')),
                ('Order_No', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Orders.orders')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='UserAccounts.account')),
            ],
        ),
        migrations.CreateModel(
            name='Terms_Conditions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Terms_and_Condition1', models.CharField(blank=True, help_text='optional', max_length=70, null=True)),
                ('Terms_and_Condition2', models.CharField(blank=True, help_text='optional', max_length=70, null=True)),
                ('Terms_and_Condition3', models.CharField(blank=True, help_text='optional', max_length=70, null=True)),
                ('Terms_and_Condition4', models.CharField(blank=True, help_text='optional', max_length=70, null=True)),
                ('Invoice_No', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Orders.invoices')),
            ],
        ),
        migrations.CreateModel(
            name='Payment_Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Received_Amount', models.FloatField(blank=True, help_text='received payment against this order', max_length=20, null=True)),
                ('Payment_Type', models.CharField(blank=True, choices=[('Due', 'Due'), ('Advance', 'Advance')], max_length=20, null=True)),
                ('Payment_Date', models.DateTimeField(blank=True, help_text='payment received date', null=True)),
                ('As_Advance_Amount', models.FloatField(blank=True, help_text='If any as advance after clear all bills', max_length=20, null=True)),
                ('Next_Commitment_Date', models.DateField(blank=True, help_text='specify if any next payment commitment date', null=True)),
                ('Invoice_No', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Orders.invoices')),
                ('Order_No', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Orders.orders')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='UserAccounts.account')),
            ],
        ),
        migrations.AddField(
            model_name='orders',
            name='Payment_Status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Orders.payment_status'),
        ),
        migrations.AddField(
            model_name='orders',
            name='Related_Project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.projects'),
        ),
        migrations.AddField(
            model_name='orders',
            name='Work_Status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Orders.work_status'),
        ),
        migrations.AddField(
            model_name='orders',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='UserAccounts.account'),
        ),
    ]
