# Generated by Django 3.2.8 on 2022-06-29 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0002_rename_po_no_format_no_formats_no_format'),
        ('Products', '0002_alter_purchases_warranty_in'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchases',
            name='PO_No_Format',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('No_Format_Related_To__in', ['PO']), _negated=True), null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.no_formats'),
        ),
    ]