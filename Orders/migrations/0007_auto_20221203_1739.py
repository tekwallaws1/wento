# Generated by Django 3.2 on 2022-12-03 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserAccounts', '0027_auto_20221119_1230'),
        ('Orders', '0006_auto_20221203_1112'),
    ]

    operations = [
        migrations.CreateModel(
            name='UPI_Accounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('UPI_Holder_Name', models.CharField(blank=True, help_text='UPI Holder Name', max_length=50, null=True)),
                ('UPI_Mobile_Number', models.CharField(blank=True, help_text='UPI Linked Mobile Number', max_length=20, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='UserAccounts.account')),
            ],
        ),
        migrations.AddField(
            model_name='payment_status',
            name='UPI_Account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Orders.upi_accounts'),
        ),
    ]
