# Generated by Django 3.2.8 on 2022-06-30 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0009_auto_20220630_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchases',
            name='Delivery_Status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Products.po_delivery_status'),
        ),
    ]
