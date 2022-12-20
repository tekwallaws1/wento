# Generated by Django 3.2.8 on 2022-10-14 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0003_alter_quotes_quote_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor_invoices',
            name='Adjusted_Amount',
            field=models.FloatField(blank=True, help_text='payment against another invoice if exceed, excess amount adjusted to this', max_length=10, null=True),
        ),
    ]
