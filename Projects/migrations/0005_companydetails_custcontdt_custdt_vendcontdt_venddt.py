# Generated by Django 3.2.8 on 2022-05-02 17:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0004_alter_projects_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=40, null=True)),
                ('Address_Line_1', models.CharField(blank=True, help_text='Address Line 1', max_length=40, null=True)),
                ('Address_Line_2', models.CharField(blank=True, help_text='Address Line 2', max_length=35, null=True)),
                ('State', models.CharField(choices=[('Andhra Pradesh', 'Andhra Pradesh'), ('Telangana', 'Telangana'), ('Tamil Nadu', 'Tamil Nadu'), ('Karnataka', 'Karnataka'), ('Maharashtra', 'Maharashtra'), ('Kerala', 'Kerala'), ('Chhattisgarh', 'Chhattisgarh'), ('Delhi', 'Delhi'), ('Goa', 'Goa'), ('Gujarat', 'Gujarat'), ('Punjab', 'Punjab'), ('Rajasthan', 'Rajasthan'), ('Haryana', 'Haryana'), ('West Bengal', 'West Bengal'), ('Himachal Pradesh', 'Himachal Pradesh'), ('Jammu and Kashmir ', 'Jammu and Kashmir '), ('Jharkhand', 'Jharkhand'), ('Arunachal Pradesh ', 'Arunachal Pradesh '), ('Assam', 'Assam'), ('Bihar', 'Bihar'), ('Madhya Pradesh', 'Madhya Pradesh'), ('Manipur', 'Manipur'), ('Meghalaya', 'Meghalaya'), ('Mizoram', 'Mizoram'), ('Nagaland', 'Nagaland'), ('Odisha', 'Odisha'), ('Sikkim', 'Sikkim'), ('Tripura', 'Tripura'), ('Uttar Pradesh', 'Uttar Pradesh'), ('Uttarakhand', 'Uttarakhand'), ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'), ('Chandigarh', 'Chandigarh'), ('Dadra and Nagar Haveli', 'Dadra and Nagar Haveli'), ('Daman and Diu', 'Daman and Diu'), ('Lakshadweep', 'Lakshadweep'), ('Puducherry', 'Puducherry')], max_length=50, null=True)),
                ('GST_No', models.CharField(blank=True, help_text='Provide If Company under GST', max_length=15, null=True)),
                ('Phone_Number_1', models.CharField(help_text='Main Phone Number', max_length=20, null=True)),
                ('Phone_Number_2', models.CharField(blank=True, help_text='Optional Phone Number', max_length=10, null=True)),
                ('Email', models.EmailField(help_text='Company Contact Mail Address', max_length=40, null=True)),
                ('Website', models.CharField(blank=True, max_length=40, null=True)),
                ('Address_Type', models.CharField(blank=True, choices=[('Billing', 'Billing'), ('Shipping', 'Shipping'), ('Branch', 'Branch'), ('Manufacturing', 'Manufacturing'), ('Service', 'Service')], max_length=40, null=True)),
                ('Active_From', models.DateField(blank=True, help_text='If leave this, it will take today date', null=True)),
                ('Status', models.BooleanField(default=True, help_text='Unmark if Company Address not in Active')),
                ('ds', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustDt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Customer_Name', models.CharField(help_text='Customer/Company Name', max_length=50, null=True)),
                ('Short_Name', models.CharField(help_text='Give Short Name for Customer, Max 15 Characters', max_length=15, null=True)),
                ('Address_Line_1', models.CharField(blank=True, help_text='Address Line 1', max_length=40, null=True)),
                ('Address_Line_2', models.CharField(blank=True, help_text='Address Line 2', max_length=35, null=True)),
                ('State', models.CharField(choices=[('Andhra Pradesh', 'Andhra Pradesh'), ('Telangana', 'Telangana'), ('Tamil Nadu', 'Tamil Nadu'), ('Karnataka', 'Karnataka'), ('Maharashtra', 'Maharashtra'), ('Kerala', 'Kerala'), ('Chhattisgarh', 'Chhattisgarh'), ('Delhi', 'Delhi'), ('Goa', 'Goa'), ('Gujarat', 'Gujarat'), ('Punjab', 'Punjab'), ('Rajasthan', 'Rajasthan'), ('Haryana', 'Haryana'), ('West Bengal', 'West Bengal'), ('Himachal Pradesh', 'Himachal Pradesh'), ('Jammu and Kashmir ', 'Jammu and Kashmir '), ('Jharkhand', 'Jharkhand'), ('Arunachal Pradesh ', 'Arunachal Pradesh '), ('Assam', 'Assam'), ('Bihar', 'Bihar'), ('Madhya Pradesh', 'Madhya Pradesh'), ('Manipur', 'Manipur'), ('Meghalaya', 'Meghalaya'), ('Mizoram', 'Mizoram'), ('Nagaland', 'Nagaland'), ('Odisha', 'Odisha'), ('Sikkim', 'Sikkim'), ('Tripura', 'Tripura'), ('Uttar Pradesh', 'Uttar Pradesh'), ('Uttarakhand', 'Uttarakhand'), ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'), ('Chandigarh', 'Chandigarh'), ('Dadra and Nagar Haveli', 'Dadra and Nagar Haveli'), ('Daman and Diu', 'Daman and Diu'), ('Lakshadweep', 'Lakshadweep'), ('Puducherry', 'Puducherry')], max_length=50, null=True)),
                ('GST_No', models.CharField(blank=True, help_text='Provide If Company under GST', max_length=15, null=True)),
                ('Phone_Number_1', models.CharField(help_text='Main Contact Phone Number', max_length=20, null=True)),
                ('Phone_Number_2', models.CharField(blank=True, help_text='Optional/Alternative Phone Number', max_length=20, null=True)),
                ('Email', models.EmailField(blank=True, help_text='Customer/Company Contact Mail Address', max_length=40, null=True)),
                ('Website', models.CharField(blank=True, help_text='Provide If have ofiicial website', max_length=40, null=True)),
                ('Address_Type', models.CharField(choices=[('Billing', 'Billing'), ('Shipping', 'Shipping'), ('Branch', 'Branch'), ('Manufacturing', 'Manufacturing'), ('Service', 'Service')], max_length=40, null=True)),
                ('Status', models.BooleanField(default=True, help_text='Unmark if Company is not in Active')),
                ('Active_From', models.DateField(blank=True, help_text='If leave this, it will take today date', null=True)),
                ('ds', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='VendDt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Supplier_Name', models.CharField(help_text='Vendor/Supplier Name', max_length=50, null=True)),
                ('Short_Name', models.CharField(help_text='Give Short Name for Supplier, Max 15 Characters', max_length=15, null=True)),
                ('Address_Line_1', models.CharField(blank=True, help_text='Address Line 1', max_length=40, null=True)),
                ('Address_Line_2', models.CharField(blank=True, help_text='Address Line 2', max_length=35, null=True)),
                ('State', models.CharField(choices=[('Andhra Pradesh', 'Andhra Pradesh'), ('Telangana', 'Telangana'), ('Tamil Nadu', 'Tamil Nadu'), ('Karnataka', 'Karnataka'), ('Maharashtra', 'Maharashtra'), ('Kerala', 'Kerala'), ('Chhattisgarh', 'Chhattisgarh'), ('Delhi', 'Delhi'), ('Goa', 'Goa'), ('Gujarat', 'Gujarat'), ('Punjab', 'Punjab'), ('Rajasthan', 'Rajasthan'), ('Haryana', 'Haryana'), ('West Bengal', 'West Bengal'), ('Himachal Pradesh', 'Himachal Pradesh'), ('Jammu and Kashmir ', 'Jammu and Kashmir '), ('Jharkhand', 'Jharkhand'), ('Arunachal Pradesh ', 'Arunachal Pradesh '), ('Assam', 'Assam'), ('Bihar', 'Bihar'), ('Madhya Pradesh', 'Madhya Pradesh'), ('Manipur', 'Manipur'), ('Meghalaya', 'Meghalaya'), ('Mizoram', 'Mizoram'), ('Nagaland', 'Nagaland'), ('Odisha', 'Odisha'), ('Sikkim', 'Sikkim'), ('Tripura', 'Tripura'), ('Uttar Pradesh', 'Uttar Pradesh'), ('Uttarakhand', 'Uttarakhand'), ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'), ('Chandigarh', 'Chandigarh'), ('Dadra and Nagar Haveli', 'Dadra and Nagar Haveli'), ('Daman and Diu', 'Daman and Diu'), ('Lakshadweep', 'Lakshadweep'), ('Puducherry', 'Puducherry')], max_length=50, null=True)),
                ('GST_No', models.CharField(blank=True, help_text='Provide If Company under GST', max_length=15, null=True)),
                ('Phone_Number_1', models.CharField(help_text='Main Contact Phone Number', max_length=20, null=True)),
                ('Phone_Number_2', models.CharField(blank=True, help_text='Optional/Alternative Phone Number', max_length=20, null=True)),
                ('Email', models.EmailField(blank=True, help_text='Customer/Company Contact Mail Address', max_length=40, null=True)),
                ('Website', models.CharField(blank=True, help_text='Provide If have ofiicial website', max_length=40, null=True)),
                ('Address_Type', models.CharField(choices=[('Billing', 'Billing'), ('Shipping', 'Shipping'), ('Branch', 'Branch'), ('Manufacturing', 'Manufacturing'), ('Service', 'Service')], max_length=40, null=True)),
                ('Supplier_Product_Details', models.TextField(blank=True, help_text='Supplier Product Details - Shortly', max_length=200, null=True)),
                ('Status', models.BooleanField(default=True, help_text='Unmark if Supplier is not in Active')),
                ('Active_From', models.DateField(blank=True, help_text='If leave this, it will take today date', null=True)),
                ('ds', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='VendContDt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Contact_Person', models.CharField(help_text='Contact Person Name', max_length=30, null=True)),
                ('Email', models.EmailField(blank=True, help_text='Contact Person Email', max_length=50, null=True)),
                ('Phone_Number_1', models.CharField(help_text='Main Contact Phone Number', max_length=20, null=True)),
                ('Phone_Number_2', models.CharField(blank=True, help_text='Optional/Alternative Phone Number', max_length=20, null=True)),
                ('Designation', models.CharField(blank=True, help_text='Specify if any', max_length=30, null=True)),
                ('Department', models.CharField(blank=True, help_text='Specify if any', max_length=30, null=True)),
                ('Other_Info', models.TextField(blank=True, help_text='Specify if want to give extra info.', max_length=200, null=True)),
                ('ds', models.BooleanField(default=True)),
                ('Supplier_Name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Projects.custdt')),
            ],
        ),
        migrations.CreateModel(
            name='CustContDt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Contact_Person', models.CharField(help_text='Contact Person Name', max_length=30, null=True)),
                ('Email', models.EmailField(blank=True, help_text='Contact Person Email', max_length=50, null=True)),
                ('Phone_Number_1', models.CharField(help_text='Main Contact Phone Number', max_length=20, null=True)),
                ('Phone_Number_2', models.CharField(blank=True, help_text='Optional/Alternative Phone Number', max_length=20, null=True)),
                ('Designation', models.CharField(blank=True, help_text='Specify if any', max_length=30, null=True)),
                ('Department', models.CharField(blank=True, help_text='Specify if any', max_length=30, null=True)),
                ('Other_Info', models.TextField(blank=True, help_text='Specify if want to give extra info.', max_length=200, null=True)),
                ('ds', models.BooleanField(default=True)),
                ('Customer_Name', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Projects.custdt')),
            ],
        ),
    ]