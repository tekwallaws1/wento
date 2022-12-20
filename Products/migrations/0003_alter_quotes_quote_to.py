# Generated by Django 3.2.8 on 2022-10-13 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0014_rename_bal_customer_vendor_ledger_bal_vendor'),
        ('Products', '0002_alter_quotes_quote_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quotes',
            name='Quote_To',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('Address_Type__in', ['Billing'])), null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.custdt'),
        ),
    ]
