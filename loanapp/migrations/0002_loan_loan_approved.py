# Generated by Django 5.2.1 on 2025-06-02 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loanapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='loan_approved',
            field=models.BooleanField(default=False),
        ),
    ]
