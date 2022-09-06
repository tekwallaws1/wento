# Generated by Django 3.2.8 on 2022-07-29 22:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserAccounts', '0011_rename_revised_date_empl_salary_revisions_revision_date'),
        ('Products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchases',
            name='Contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contact', to='UserAccounts.account'),
        ),
    ]