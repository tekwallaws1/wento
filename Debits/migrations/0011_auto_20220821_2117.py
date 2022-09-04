# Generated by Django 3.2.8 on 2022-08-21 21:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserAccounts', '0015_empl_salaries_effective_from'),
        ('Debits', '0010_alter_expenses_reference_no'),
    ]

    operations = [
        migrations.RenameField(
            model_name='monthly_salaries',
            old_name='ESI_Employee',
            new_name='ESI',
        ),
        migrations.RenameField(
            model_name='monthly_salaries',
            old_name='PF_Employee',
            new_name='PF',
        ),
        migrations.RenameField(
            model_name='monthly_salaries',
            old_name='Advance',
            new_name='Salary_Advance',
        ),
        migrations.RenameField(
            model_name='monthly_salaries',
            old_name='Income_Tax_Deductions',
            new_name='TDS',
        ),
        migrations.RemoveField(
            model_name='monthly_salaries',
            name='Attendance',
        ),
        migrations.RemoveField(
            model_name='monthly_salaries',
            name='ESI_Employer',
        ),
        migrations.RemoveField(
            model_name='monthly_salaries',
            name='PF_Employer',
        ),
        migrations.RemoveField(
            model_name='monthly_salaries',
            name='Salary',
        ),
        migrations.AddField(
            model_name='monthly_salaries',
            name='Last_Updated_Date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='monthly_salaries',
            name='Month',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='monthly_salaries',
            name='Name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='UserAccounts.account'),
        ),
        migrations.AlterField(
            model_name='debit_amounts',
            name='Against',
            field=models.CharField(blank=True, choices=[('Travel', 'Travel'), ('Food', 'Food'), ('Lodging', 'Lodging'), ('Fuel', 'Fuel'), ('Repair', 'Repair'), ('Transportation', 'Transportation'), ('Recharges', 'Recharges'), ('Stationery', 'Stationery'), ('General Purchase', 'General Purchase'), ('Miscellaneous', 'Miscellaneous')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='exp_items',
            name='Category',
            field=models.CharField(choices=[('Travel', 'Travel'), ('Food', 'Food'), ('Lodging', 'Lodging'), ('Fuel', 'Fuel'), ('Repair', 'Repair'), ('Transportation', 'Transportation'), ('Recharges', 'Recharges'), ('Stationery', 'Stationery'), ('General Purchase', 'General Purchase'), ('Miscellaneous', 'Miscellaneous')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='expenses',
            name='Related_To',
            field=models.CharField(choices=[('Services', 'Services'), ('Supplies', 'Supplies'), ('Factory', 'Factory'), ('Marketing', 'Marketing'), ('Office', 'Office'), ('Dispatches', 'Dispatches'), ('Others', 'Others')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='monthly_salaries',
            name='LOP',
            field=models.FloatField(blank=True, help_text='loss of pay if eligible', max_length=10, null=True),
        ),
    ]
