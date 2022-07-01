# Generated by Django 3.2.8 on 2022-06-29 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0002_rename_po_no_format_no_formats_no_format'),
        ('Orders', '0004_invoices_fy'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoices',
            name='Invoice_No_Format',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('No_Format_Related_To__in', ['Invoice']), _negated=True), null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.no_formats'),
        ),
    ]
