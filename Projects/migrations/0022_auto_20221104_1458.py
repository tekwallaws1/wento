# Generated by Django 3.2.8 on 2022-11-04 14:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0021_auto_20221104_1449'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page_permissions',
            name='Edit_Permissions',
        ),
        migrations.RemoveField(
            model_name='page_permissions',
            name='RC',
        ),
        migrations.RemoveField(
            model_name='page_permissions',
            name='Related_Project',
        ),
        migrations.RemoveField(
            model_name='page_permissions',
            name='View_Permissions',
        ),
        migrations.RemoveField(
            model_name='view_pages',
            name='RC',
        ),
        migrations.RemoveField(
            model_name='view_pages',
            name='Related_Project',
        ),
        migrations.DeleteModel(
            name='Edit_Pages',
        ),
        migrations.DeleteModel(
            name='Page_Permissions',
        ),
        migrations.DeleteModel(
            name='View_Pages',
        ),
    ]
