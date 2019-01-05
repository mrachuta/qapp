# Generated by Django 2.1.3 on 2018-12-30 23:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qapp', '0017_auto_20181230_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 31, 0, 36, 59, 491469)),
        ),
        migrations.AlterField(
            model_name='gate',
            name='car',
            field=models.CharField(choices=[('C1', 'C1'), ('C2', 'C2'), ('C3', 'C3'), ('C4', 'C4')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='gate',
            name='creation_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2018, 12, 31, 0, 36, 59, 489467)),
        ),
        migrations.AlterField(
            model_name='gate',
            name='type',
            field=models.CharField(choices=[('BJC', 'Bramka jakościowa - człon'), ('BJW', 'Bramka jakościowa - wózek'), ('IKS', 'Inspekcja końcowa - Solaris'), ('IKK', 'Inspekcja końcowa - klient')], default='BJC', max_length=3),
        ),
        migrations.AlterField(
            model_name='log',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 31, 0, 36, 59, 492470)),
        ),
        migrations.AlterField(
            model_name='operationarea',
            name='area',
            field=models.CharField(choices=[('KLE', 'Klejownia'), ('KAB', 'Kablownia'), ('PDM', 'Podmontaż dachów - mechanika'), ('PDE', 'Podmontaż dachów - elektryka'), ('MGM', 'Montaż główny - mechanika'), ('MGE', 'Montaż główny - elektryka'), ('MKM', 'Montaż końcowy - mechanika'), ('MKE', 'Montaż końcowy - elektryka'), ('MWM', 'Montaż wózków - mechanika'), ('MWE', 'Montaż wózków - elektryka'), ('MKA', 'Montaż kabin'), ('TES', 'Testing'), ('ISD', 'Inspekcja końcowa Solaris - dach'), ('ISP', 'Inspekcja końcowa Solaris - podwozie'), ('ISW', 'Inspekcja końcowa Solaris - wnętrzne'), ('ISZ', 'Inspekcja końcowa Solaris - zewnątrz'), ('ISL', 'Inspekcja końcowa Solaris - lakier'), ('IKT', 'Inspekcja końcowa klienta - tramwaj')], max_length=3),
        ),
    ]
