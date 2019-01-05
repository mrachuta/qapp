# Generated by Django 2.1.3 on 2018-12-18 19:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='category',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AlterField(
            model_name='comment',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 18, 20, 39, 17, 171773)),
        ),
        migrations.AlterField(
            model_name='log',
            name='action',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='log',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 18, 20, 39, 17, 172773)),
        ),
    ]
