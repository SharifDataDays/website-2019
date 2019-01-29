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
    trial_duration = models.IntegerField(null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    scoreboard_freeze_time = models.DateTimeField(null=True, blank=True)
    current_trial_id = models.IntegerField(default=0)

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
    CHOICES = (
        ('difficult', _('difficult')),
        ('medium', _('medium')),
        ('easy', _('easy'))
    )
    stmt = models.CharField(max_length=500)
    value = models.CharField(max_length=200, null=True, blank=True)
    correct_answer = models.CharField(max_length=200)
    score = models.FloatField(default=0, null=True)
    type = models.CharField(max_length=200, blank=True)
    level = models.CharField(max_length=200 , choices=CHOICES, blank=True, null=True)

    def __str__(self):
        return str('%s: %s' % (self.type, self.stmt))


class MultipleChoiceQuestion(Question):

    def save(self):
        self.type = 'MultipleChoiceQuestion'
        super(MultipleChoiceQuestion, self).save()


class Choice(models.Model):
    text = models.CharField(max_length=200)
    question = models.ForeignKey(MultipleChoiceQuestion, related_name='choices')


class FileUploadQuestion(Question):
    download_url = models.CharField(max_length=200)
    upload_url = models.CharField(max_length=200)

    def save(self, **kwargs):
        self.type = 'FileUploadQuestion'
        super(FileUploadQuestion, self).save()


class RangeAcceptQuestion(Question):
    min_range = models.FloatField()
    max_range = models.FloatField()

    def save(self):
        self.type = 'RangeAcceptQuestion'
        super(RangeAcceptQuestion, self).save()


class MultipleAnswerQuestion(Question):
    def save(self):
        self.type = 'MultipleAnswerQuestion'
        super(MultipleAnswerQuestion, self).save()


class Answer(models.Model):
    text = models.CharField(max_length=200)
    question = models.ForeignKey(MultipleAnswerQuestion)


class Trial(models.Model):
    questions = models.ManyToManyField(Question, blank=True)
    competition = models.ForeignKey(Competition)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    submit_time = models.DateTimeField(null=True)
    score = models.FloatField(default=0)
    team = models.ForeignKey(TeamParticipatesChallenge, related_name='trials', null=True)

    def save(self, *args, **kwargs):
        super(Trial, self).save()
        self.end_time = self.start_time + datetime.timedelta(hours=self.competition.trial_duration)
        super(Trial, self).save()

    def __str__(self):
        return str('%s Trial number %d' %(self.competition, self.id))


class PhaseInstructionSet(models.Model):
    phase = models.OneToOneField(Competition)

    def __str__(self):
        return str('%s InstructionSet' % self.phase)


class Instruction(models.Model):
    CHOICES = (
        ('difficult', _('difficult')),
        ('medium', _('medium')),
        ('easy', _('easy'))
    )
    type = models.CharField(max_length=200)
    app = models.CharField(max_length=200)
    level = models.CharField(max_length=200, choices=CHOICES)
    number = models.IntegerField()
    phase_instruction_set = models.ForeignKey(PhaseInstructionSet)

    def __str__(self):
        return str('%s : %s' % (self.type ,self.number))


def get_log_file_directory(instance, filename):
    return os.path.join('logs', filename + str(uuid.uuid4()))
