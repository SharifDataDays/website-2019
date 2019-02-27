# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-02-27 04:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0048_auto_20190226_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamparticipateschallenge',
            name='paid_amount',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='teamparticipateschallenge',
            name='payment_last_time_checked',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]