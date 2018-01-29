# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-24 21:51
from __future__ import unicode_literals

import apps.game.models.competition
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20180118_2123'),
    ]

    operations = [
        migrations.CreateModel(
            name='SingleMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('done', models.BooleanField(default=False)),
                ('infra_match_message', models.CharField(blank=True, max_length=1023, null=True)),
                ('infra_token', models.CharField(blank=True, max_length=256, null=True, unique=True)),
                ('log', models.FileField(blank=True, null=True, upload_to=apps.game.models.competition.get_log_file_directory)),
                ('part1_score', models.IntegerField(blank=True, null=True)),
                ('part2_score', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='match',
            options={'verbose_name_plural': 'matches'},
        ),
        migrations.AlterModelOptions(
            name='teamparticipateschallenge',
            options={'verbose_name_plural': 'Team Participates In Challenges'},
        ),
        migrations.RemoveField(
            model_name='match',
            name='done',
        ),
        migrations.RemoveField(
            model_name='match',
            name='infra_match_message',
        ),
        migrations.RemoveField(
            model_name='match',
            name='infra_token',
        ),
        migrations.RemoveField(
            model_name='match',
            name='log',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='score',
        ),
        migrations.AddField(
            model_name='teamsubmission',
            name='infra_compile_token',
            field=models.CharField(blank=True, max_length=256, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='teamsubmission',
            name='status',
            field=models.CharField(choices=[('uploading', 'Uploading'), ('uploaded', 'Uploaded'), ('compiling', 'Compiling'), ('compiled', 'Compiled')], default='uploading', max_length=128),
        ),
        migrations.AlterField(
            model_name='match',
            name='competition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='game.Competition'),
        ),
        migrations.AlterField(
            model_name='teamsubmission',
            name='language',
            field=models.CharField(choices=[('c++', 'C++'), ('java', 'Java'), ('python2', 'Python 2'), ('python3', 'Python 3')], default='java', max_length=128),
        ),
        migrations.AddField(
            model_name='singlematch',
            name='match',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='single_matches', to='game.Match'),
        ),
    ]