# Generated by Django 3.2.8 on 2022-06-29 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0003_auto_20220628_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoices',
            name='FY',
            field=models.CharField(blank=True, help_text='financial year such as 22-23, 23-24 etc..', max_length=10, null=True),
        ),
    ]