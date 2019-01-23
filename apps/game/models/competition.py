import codecs
import json

import uuid

import os
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpResponseServerError, Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext
import datetime

from apps.accounts.models import Team
from apps.game.models.challenge import Challenge, TeamSubmission, TeamParticipatesChallenge

import logging

logger = logging.getLogger(__name__)


class Competition(models.Model):
    challenge = models.ForeignKey(Challenge, related_name='competitions')
    name = models.CharField(max_length=128, null=True)
    tag = models.CharField(max_length=128, null=True)
    trial_time = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    scoreboard_freeze_time = models.DateTimeField(null=True, blank=True)

    def get_freeze_time(self):
        if self.scoreboard_freeze_time is not None:
            return self.scoreboard_freeze_time
        return self.challenge.scoreboard_freeze_time

    def save(self):
        super(Competition, self).save()
        # TODO: write save

    def __str__(self):
        if self.name is None:
            return str(self.id)
        return str(self.name)


class Question(models.Model):
    stmt = models.CharField(max_length=500)
    value = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=200)
    score = models.FloatField()


class MultipleChoiceQuestion(Question):
    choice1 = models.CharField(max_length=200)
    choice2 = models.CharField(max_length=200)
    choice3 = models.CharField(max_length=200)
    choice4 = models.CharField(max_length=200)


class FileUploadQuestion(Question):
    download_url = models.CharField(max_length=200)
    upload_url = models.CharField(max_length=200)


class RangeAcceptQuestion(Question):
    min_range = models.FloatField()
    max_range = models.FloatField()


class MultipleAnswerQuestion(Question):
    pass


class Answer(models.Model):
    text = models.CharField(max_length=200)
    question = models.ForeignKey(MultipleChoiceQuestion)


class Trial(models.Model):
    questions = models.ManyToManyField(Question, blank=True)
    competition = models.ForeignKey(Competition)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    score = models.FloatField()
    team = models.ForeignKey(TeamParticipatesChallenge)

    def save(self):
        self.end_time += self.datetime.timedelta(hours=self.competition.trial_time)


def get_log_file_directory(instance, filename):
    return os.path.join('logs', filename + str(uuid.uuid4()))
