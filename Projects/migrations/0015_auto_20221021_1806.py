# Generated by Django 3.2.8 on 2022-10-21 18:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0014_rename_bal_customer_vendor_ledger_bal_vendor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bank_accounts',
            name='Related_Company',
        ),
        migrations.AddField(
            model_name='bank_accounts',
            name='RC',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails'),
        ),
        migrations.AddField(
            model_name='companydetails',
            name='Short_Name',
            field=models.CharField(help_text='Nick Name or Short Name of Project', max_length=15, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='custdt',
            name='RC',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails'),
        ),
        migrations.AddField(
            model_name='customer_ledger',
            name='RC',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails'),
        ),
        migrations.AddField(
            model_name='no_formats',
            name='RC',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails'),
        ),
        migrations.AddField(
            model_name='projects',
            name='RC',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails'),
        ),
        migrations.AddField(
            model_name='venddt',
            name='RC',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails'),
        ),
        migrations.AddField(
            model_name='vendor_ledger',
            name='RC',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails'),
        ),
    ]
