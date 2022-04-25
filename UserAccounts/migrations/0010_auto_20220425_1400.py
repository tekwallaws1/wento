# Generated by Django 3.2.8 on 2022-04-25 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserAccounts', '0009_alter_permissions_expenses_dashboard'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='Firsr_Name',
            field=models.CharField(blank=True, help_text='Nick Name or Short Name', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='Last_Name',
            field=models.CharField(blank=True, help_text='Nick Name or Short Name', max_length=10, null=True),
        ),
    ]
