# Generated by Django 3.2.8 on 2022-07-02 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0014_alter_purchases_delivery_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchases',
            old_name='Delivery_Status',
            new_name='Delivery_Update',
        ),
        migrations.AlterField(
            model_name='po_delivery_status',
            name='Next_Commitment_Date',
            field=models.DateField(blank=True, help_text='yyyy-mm-dd', null=True),
        ),
        migrations.AlterField(
            model_name='po_delivery_status',
            name='PO_No',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Products.purchases'),
        ),
        migrations.AlterField(
            model_name='vendor_invoices',
            name='PO_No',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Products.purchases'),
        ),
        migrations.AlterField(
            model_name='vendor_payment_status',
            name='PO_No',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Products.purchases'),
        ),
    ]