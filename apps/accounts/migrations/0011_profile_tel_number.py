# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-21 11:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20180219_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='tel_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
