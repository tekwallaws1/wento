# Generated by Django 3.2.8 on 2022-08-29 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Debits', '0013_auto_20220827_2211'),
    ]

    operations = [
        migrations.CreateModel(
            name='Month_Sal_Exp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Month', models.DateField(blank=True, null=True)),
                ('Issued_Salareis', models.IntegerField(blank=True, help_text='total issued salaries', null=True)),
                ('Pending_Salaries', models.IntegerField(blank=True, help_text='pending salaries', null=True)),
                ('Issued_Date', models.DateField(help_text='salary issued date', null=True)),
                ('Total_LOP', models.FloatField(blank=True, help_text='loss of pay if eligible', max_length=10, null=True)),
                ('Total_OT', models.IntegerField(blank=True, help_text='over time amount if eligible', null=True)),
                ('Paid_PF', models.FloatField(blank=True, default=0, help_text='PF employee share 12% of basic if eligible', max_length=10, null=True)),
                ('Paid_ESI', models.FloatField(blank=True, default=0, help_text='3.25% employer on gross', max_length=10, null=True)),
                ('Total_Paid', models.FloatField(blank=True, default=0, help_text='PT deductions if eligible, <15K 0, 15-20K 150, >15K 200 of gross', max_length=10, null=True)),
                ('Total_TDS', models.FloatField(blank=True, default=0, help_text='TDS/income tax deductions if eligible', max_length=10, null=True)),
                ('Other_Deductions', models.FloatField(blank=True, default=0, help_text='other deductions', max_length=10, null=True)),
                ('Total_Advances', models.FloatField(blank=True, default=0, help_text='advances with employes', max_length=10, null=True)),
                ('Last_Updated_Date', models.DateField(blank=True, null=True)),
            ],
        ),
    ]
