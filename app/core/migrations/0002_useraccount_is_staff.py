# Generated by Django 3.2.4 on 2021-06-23 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='is_staff',
            field=models.BooleanField(default=False, verbose_name='is_staff'),
        ),
    ]
