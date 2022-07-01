# Generated by Django 3.2.8 on 2022-06-29 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0002_rename_po_no_format_no_formats_no_format'),
    ]

    operations = [
        migrations.AlterField(
            model_name='no_formats',
            name='No_Format_Related_To',
            field=models.CharField(choices=[('Invoice', 'Invoice'), ('Proforma Invoice', 'Proforma Invoice'), ('PO', 'PO'), ('DC', 'DC'), ('Expenses Voucher', 'Expenses Voucher')], max_length=20, null=True),
        ),
    ]