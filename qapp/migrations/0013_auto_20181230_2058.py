# Generated by Django 2.1.3 on 2018-12-30 19:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qapp', '0012_auto_20181230_2058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 30, 20, 58, 12, 481423)),
        ),
        migrations.AlterField(
            model_name='gate',
            name='creation_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2018, 12, 30, 20, 58, 12, 479421)),
        ),
        migrations.AlterField(
            model_name='log',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 30, 20, 58, 12, 483425)),
        ),
    ]
