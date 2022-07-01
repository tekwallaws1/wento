# Generated by Django 3.2.8 on 2022-06-29 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0003_alter_no_formats_no_format_related_to'),
        ('Products', '0003_purchases_po_no_format'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchases',
            name='Is_Billed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='purchases',
            name='PO_No_Format',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('No_Format_Related_To__in', ['PO'])), null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.no_formats'),
        ),
    ]
