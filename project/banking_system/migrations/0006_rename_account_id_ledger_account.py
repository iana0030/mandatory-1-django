# Generated by Django 4.1.1 on 2022-10-07 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banking_system', '0005_alter_customer_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ledger',
            old_name='account_id',
            new_name='account',
        ),
    ]
