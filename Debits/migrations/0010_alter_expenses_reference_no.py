# Generated by Django 3.2.8 on 2022-08-09 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Debits', '0009_auto_20220808_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenses',
            name='Reference_No',
            field=models.CharField(blank=True, help_text='voucher no', max_length=20, null=True, unique=True),
        ),
    ]