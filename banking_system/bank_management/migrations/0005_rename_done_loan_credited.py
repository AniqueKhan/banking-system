# Generated by Django 3.2.18 on 2023-03-29 21:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bank_management', '0004_loan_done'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loan',
            old_name='done',
            new_name='credited',
        ),
    ]
