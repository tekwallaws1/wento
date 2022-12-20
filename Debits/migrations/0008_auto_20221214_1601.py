# Generated by Django 3.2 on 2022-12-14 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0026_alter_bank_accounts_account_type'),
        ('Debits', '0007_auto_20221208_2202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='debit_amounts',
            name='Payment_Mode',
        ),
        migrations.AddField(
            model_name='debit_amounts',
            name='Account_Name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.bank_accounts'),
        ),
    ]
