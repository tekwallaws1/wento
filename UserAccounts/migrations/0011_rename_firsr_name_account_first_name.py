# Generated by Django 3.2.8 on 2022-04-25 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserAccounts', '0010_auto_20220425_1400'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='Firsr_Name',
            new_name='First_Name',
        ),
    ]
