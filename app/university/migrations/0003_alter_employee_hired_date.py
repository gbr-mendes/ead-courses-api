# Generated by Django 3.2.11 on 2022-01-18 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('university', '0002_rename_employe_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='hired_date',
            field=models.DateField(default='2022-01-18'),
        ),
    ]