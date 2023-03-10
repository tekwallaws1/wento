# Generated by Django 3.2.16 on 2023-02-23 11:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Debits', '0001_initial'),
        ('UserAccounts', '0001_initial'),
        ('Projects', '0001_initial'),
        ('Orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expenses',
            name='Sales_Order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Orders.orders'),
        ),
        migrations.AddField(
            model_name='expenses',
            name='Submitted_By',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submittedby', to='UserAccounts.account'),
        ),
        migrations.AddField(
            model_name='exp_items',
            name='Expenses',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Debits.expenses'),
        ),
        migrations.AddField(
            model_name='declaredayas',
            name='RC',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails'),
        ),
        migrations.AddField(
            model_name='debit_amounts',
            name='Account_Name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.bank_accounts'),
        ),
        migrations.AddField(
            model_name='debit_amounts',
            name='Approved_By',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='amountapprovedby', to='UserAccounts.account'),
        ),
        migrations.AddField(
            model_name='debit_amounts',
            name='Employ',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ifemploy', to='UserAccounts.account'),
        ),
        migrations.AddField(
            model_name='debit_amounts',
            name='Expenses',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Debits.expenses'),
        ),
        migrations.AddField(
            model_name='debit_amounts',
            name='Issued_By',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issuedamountby', to='UserAccounts.account'),
        ),
        migrations.AddField(
            model_name='debit_amounts',
            name='Issued_To',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='UserAccounts.account'),
        ),
        migrations.AddField(
            model_name='debit_amounts',
            name='RC',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails'),
        ),
        migrations.AddField(
            model_name='debit_amounts',
            name='Related_Project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.projects'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='Issued_By',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendanceissuedby', to='UserAccounts.account'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='Name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attender', to='UserAccounts.account'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='RC',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.companydetails'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='Sales_Order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Orders.orders'),
        ),
    ]
