# Generated by Django 3.2 on 2022-12-13 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0024_auto_20221213_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank_accounts',
            name='Balance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
