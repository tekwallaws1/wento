# Generated by Django 3.2.8 on 2022-06-30 19:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0011_auto_20220630_1942'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchases',
            old_name='Delivery_Status',
            new_name='Delivery_Status1',
        ),
    ]
