# Generated by Django 3.2.8 on 2022-09-20 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0010_auto_20220920_1052'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer_ledger',
            name='Order_No',
        ),
        migrations.RemoveField(
            model_name='vendor_ledger',
            name='Order_No',
        ),
    ]