# Generated by Django 3.2.8 on 2022-06-28 14:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Projects', '0001_initial'),
        ('Orders', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='FY',
            field=models.CharField(blank=True, help_text='financial year such as 22-23, 23-24 etc..', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='orders',
            name='Order_No_1',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='Customer_Name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Projects.custdt'),
        ),
    ]
