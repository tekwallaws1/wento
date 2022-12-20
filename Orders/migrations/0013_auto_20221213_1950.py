# Generated by Django 3.2 on 2022-12-13 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0024_auto_20221213_1950'),
        ('Orders', '0012_alter_orders_po_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment_status',
            name='Payment_Account',
        ),
        migrations.RemoveField(
            model_name='payment_status',
            name='UPI_Account',
        ),
        migrations.AddField(
            model_name='payment_status',
            name='Account_Name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.bank_accounts'),
        ),
    ]
