# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-01-28 14:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=11, null=True, verbose_name='Mobile number\u200c')),
                ('organization', models.CharField(max_length=128, verbose_name='Organization\u200c')),
                ('age', models.IntegerField(blank=True, null=True, verbose_name='Age\u200c')),
                ('national_code', models.CharField(blank=True, max_length=10, null=True, verbose_name='National code\u200c')),
                ('tel_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Telephone number\u200c')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='UserParticipatesOnTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='accounts.Team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
