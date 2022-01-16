# Generated by Django 3.2.11 on 2022-01-16 11:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_zip_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='type',
        ),
        migrations.AddField(
            model_name='user',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.usertype'),
        ),
    ]