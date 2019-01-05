# Generated by Django 2.1.3 on 2018-12-31 11:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qapp', '0025_auto_20181231_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 31, 12, 20, 36, 895668)),
        ),
        migrations.AlterField(
            model_name='gate',
            name='creation_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2018, 12, 31, 12, 20, 36, 893667)),
        ),
        migrations.AlterField(
            model_name='log',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 31, 12, 20, 36, 896668)),
        ),
        migrations.AlterUniqueTogether(
            name='gate',
            unique_together={('tram', 'bogie', 'car', 'area', 'operation_no')},
        ),
    ]
