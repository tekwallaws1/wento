# Generated by Django 3.2.8 on 2022-11-14 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserAccounts', '0022_auto_20221114_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='page_permissions',
            name='Edit_Permissions',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('Mode__Mode__in', ['Edit'])), null=True, related_name='edit', to='UserAccounts.Pages'),
        ),
        migrations.AlterField(
            model_name='page_permissions',
            name='View_Permissions',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('Mode__Mode__in', ['View'])), null=True, related_name='view', to='UserAccounts.Pages'),
        ),
    ]
