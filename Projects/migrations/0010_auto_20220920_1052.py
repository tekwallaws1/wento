# Generated by Django 3.2.8 on 2022-09-20 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0009_auto_20220919_2240'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer_ledger',
            old_name='Balance',
            new_name='Bal_All',
        ),
        migrations.RenameField(
            model_name='vendor_ledger',
            old_name='Balance',
            new_name='Bal_All',
        ),
        migrations.AddField(
            model_name='customer_ledger',
            name='Bal_Customer',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='vendor_ledger',
            name='Bal_Customer',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, null=True),
        ),
    ]
