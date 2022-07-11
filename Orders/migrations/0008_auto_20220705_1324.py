# Generated by Django 3.2.8 on 2022-07-05 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0007_alter_orders_po_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoices',
            name='Is_Manual',
            field=models.BooleanField(default=False, help_text='wether it is manual entry or online generation'),
        ),
        migrations.AlterField(
            model_name='invoices',
            name='Attach',
            field=models.FileField(blank=True, help_text='attach invoice copy if available', null=True, upload_to='customerinvoices/'),
        ),
        migrations.AlterField(
            model_name='invoices',
            name='GST_Amount',
            field=models.FloatField(blank=True, help_text='only GST Amount', max_length=10, null=True),
        ),
    ]