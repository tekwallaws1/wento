# Generated by Django 3.2.8 on 2022-07-28 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserAccounts', '0008_auto_20220728_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='empl_salaries',
            name='Is_Providing_PF_Employer_Share',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='empl_salaries',
            name='Net_Salary',
            field=models.IntegerField(blank=True, help_text='you can give it or we will calculate', null=True),
        ),
        migrations.AlterField(
            model_name='empl_salaries',
            name='Professional_Tax',
            field=models.FloatField(blank=True, default=0, help_text='PT deductions if eligible, <15K 0, 15-20K 150, >15K 200 of gross', max_length=10, null=True),
        ),
    ]
