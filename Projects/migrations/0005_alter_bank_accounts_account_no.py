# Generated by Django 3.2.8 on 2022-07-04 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0004_auto_20220703_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank_accounts',
            name='Account_No',
            field=models.CharField(help_text='Bank Account Number', max_length=40, null=True),
        ),
    ]
