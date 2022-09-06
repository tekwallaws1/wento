# Generated by Django 3.2.8 on 2022-07-30 16:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0001_initial'),
        ('UserAccounts', '0011_rename_revised_date_empl_salary_revisions_revision_date'),
        ('Products', '0004_alter_purchases_po_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quote_TC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Taxes', models.CharField(blank=True, help_text='Ex: GST @ 18% (As Applicable)', max_length=50, null=True)),
                ('Payment_Terms', models.CharField(blank=True, help_text='Payment terms and conditions', max_length=150, null=True)),
                ('Delivery_Terms', models.CharField(blank=True, help_text='delivery details and terms', max_length=150, null=True)),
                ('Transport_Terms', models.CharField(blank=True, help_text='included/excluded or any other', max_length=100, null=True)),
                ('Validation_Terms', models.CharField(blank=True, help_text='prices/quote validation terms', max_length=100, null=True)),
                ('FOR', models.CharField(blank=True, help_text='Ex; FOR Hyderabad', max_length=100, null=True)),
                ('Other_Terms', models.CharField(blank=True, help_text='other terms if need to specify', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Quotes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Quote_No', models.CharField(blank=True, help_text='Quote No', max_length=30, null=True)),
                ('Date', models.DateTimeField(blank=True, help_text='quote date', null=True)),
                ('Firm_Name', models.CharField(blank=True, help_text='quote to company, company name if available', max_length=50, null=True)),
                ('Reference_Person', models.CharField(blank=True, help_text='Contact Person Name', max_length=50, null=True)),
                ('Phone_Number', models.CharField(blank=True, help_text='Main Contact Phone Number', max_length=20, null=True)),
                ('Email', models.EmailField(blank=True, help_text='Contact Person Email', max_length=50, null=True)),
                ('Location', models.CharField(blank=True, help_text='location and state if available', max_length=50, null=True)),
                ('Quote_Value', models.FloatField(blank=True, help_text='excluding taxes', max_length=20, null=True)),
                ('Valid_Days', models.IntegerField(blank=True, help_text='quote validation in days such as 15, 30 etc..', null=True)),
                ('Comments', models.TextField(blank=True, help_text='anything to specify with note', max_length=500, null=True)),
                ('Thanks_Note', models.CharField(blank=True, help_text='thanks giving text', max_length=150, null=True)),
                ('Prepared_By', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preparedby', to='UserAccounts.account')),
                ('Quote_From', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails')),
                ('Quote_Submitted_By', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sbmby', to='UserAccounts.account')),
                ('Quote_To', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.custcontdt')),
                ('Related_Project', models.ForeignKey(blank=True, help_text='leave empty if product meant for many projects', null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.projects')),
            ],
        ),
        migrations.CreateModel(
            name='Quote_Items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Quantity', models.FloatField(max_length=10, null=True)),
                ('Add_Item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Products.product_price')),
                ('Quote_No', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Products.quotes')),
            ],
        ),
        migrations.CreateModel(
            name='Copy_Quote_Items',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Item_Description', models.TextField(blank=True, help_text='Item description', max_length=1000, null=True)),
                ('Quantity', models.FloatField(help_text='quantity', max_length=10, null=True)),
                ('UOM', models.CharField(choices=[('No', 'Nos'), ('Set', 'Sets'), ('Kg', 'Kgs'), ('Mtr', 'Mtrs'), ('Ltr', 'Ltrs'), ('Bag', 'Bags')], max_length=15, null=True)),
                ('Unit_Price', models.FloatField(blank=True, help_text='each unit price excluding all taxes', max_length=15, null=True)),
                ('GST', models.FloatField(blank=True, help_text='GST in % such as 12, 18 etc', max_length=5, null=True)),
                ('Item_From_Product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Products.quote_items')),
                ('Quote_No', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Products.quotes')),
            ],
        ),
    ]