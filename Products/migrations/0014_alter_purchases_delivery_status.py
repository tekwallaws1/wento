# Generated by Django 3.2.8 on 2022-06-30 19:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0013_rename_delivery_status1_purchases_delivery_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchases',
            name='Delivery_Status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Products.po_delivery_status'),
        ),
    ]