# Generated by Django 3.2.8 on 2022-07-27 23:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserAccounts', '0003_empl_salary_revisions'),
        ('Debits', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Monthly_Salaries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Issued_Salary', models.IntegerField(blank=True, help_text='issued salary or net salary for this month', null=True)),
                ('Issued_Date', models.DateField(help_text='salary issued date', null=True)),
                ('LOP', models.IntegerField(blank=True, help_text='loss of pay if eligible', null=True)),
                ('OT_Amount', models.IntegerField(blank=True, help_text='over time amount if eligible', max_length=5, null=True)),
                ('PF_Employer', models.FloatField(blank=True, default=0, help_text='PF employer share if eligible', max_length=10, null=True)),
                ('PF_Employee', models.FloatField(blank=True, default=0, help_text='PF employee share if eligible', max_length=10, null=True)),
                ('ESI_Employer', models.FloatField(blank=True, default=0, help_text='ESI employer share if eligible', max_length=10, null=True)),
                ('ESI_Employee', models.FloatField(blank=True, default=0, help_text='ESI employee share if eligible', max_length=10, null=True)),
                ('Pofessional_Tax', models.FloatField(blank=True, default=0, help_text='PT deductions if eligible', max_length=10, null=True)),
                ('Income_Tax_Deductions', models.FloatField(blank=True, default=0, help_text='TDS/income tax deductions if eligible', max_length=10, null=True)),
                ('Other_Deductions', models.FloatField(blank=True, default=0, help_text='other deductions', max_length=10, null=True)),
                ('Advance', models.FloatField(blank=True, default=0, help_text='advances with employes', max_length=10, null=True)),
                ('Issued_Status', models.BooleanField(default=True, help_text='issued status')),
                ('Status', models.BooleanField(default=True, help_text='active status')),
                ('Attendance', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Debits.monthatnd')),
                ('Salary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='UserAccounts.empl_salaries')),
            ],
        ),
    ]
