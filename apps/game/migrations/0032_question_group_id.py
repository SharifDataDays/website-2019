# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-02-01 18:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0031_remove_question_group_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='group_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]