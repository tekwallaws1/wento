# Generated by Django 3.2.8 on 2022-11-04 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0022_auto_20221104_1458'),
        ('UserAccounts', '0017_edit_pages_page_permissions_view_pages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='RC',
        ),
        migrations.AddField(
            model_name='account',
            name='RC',
            field=models.ManyToManyField(blank=True, null=True, to='Projects.CompanyDetails'),
        ),
        migrations.DeleteModel(
            name='Permissions',
        ),
    ]
