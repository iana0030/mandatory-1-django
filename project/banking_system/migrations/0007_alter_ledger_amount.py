# Generated by Django 4.1.1 on 2022-10-31 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking_system', '0006_rename_account_id_ledger_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ledger',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
    ]