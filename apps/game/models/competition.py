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

    def save(self, ):
        super(Competition, self).save()
        # TODO: write save

    def __str__(self):
        if self.name is None:
            return str(self.id)
        return str(self.name)


class Question(models.Model):
    LEVEL_CHOICES = (
        ('difficult', _('difficult')),
        ('medium', _('medium')),
        ('easy', _('easy'))
    )
    TYPE_CHOICES = (
        ('multiple_choice', _('multiple_choice')), # MultipleChoiceQuestion
        ('single_answer', _('single_answer')), # Question
        ('multiple_answer', _('multiple_answer')), # MultipleAnswerQuestion
        ('single_sufficient_answer', _('single_sufficient_answer')), # Question
        ('single_number', _('single_number')), # Question type=number specified in template
        ('interval_number', _('interval_number')), # IntervalQuestion type=number specified in template
        ('file_upload', _('file_upload')) # FileUploadQuestion
    )
    UI_TYPE_CHOICES = (
        ('text_number', _('text_number')), # single_number, interval_number
        ('text_string', _('text_string')), # single_answer, single_sufficient_answer
        ('choices', _('choices')), # multiple_choices
        ('multiple', _('multiple')), # multiple_answer
        ('file', _('file')) # file_upload
    )

    stmt = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=200)
    max_score = models.FloatField(default=0, null=True)
    type = models.CharField(max_length=200, blank=True, choices=TYPE_CHOICES)
    ui_type = models.CharField(max_length=200, blank=True, choices=UI_TYPE_CHOICES)
    level = models.CharField(max_length=200, choices=LEVEL_CHOICES, blank=True, null=True)

    def __str__(self):
        return str('%s: %s' % (self.type, self.stmt))


class MultipleChoiceQuestion(Question):

    def save(self):

        self.type = 'multiple_choice'
        self.ui_type = 'choices'
        super(MultipleChoiceQuestion, self).save()


class Choice(models.Model):
    text = models.CharField(max_length=200)
    question = models.ForeignKey(MultipleChoiceQuestion, related_name='choices')


class FileUploadQuestion(Question):
    download_url = models.CharField(max_length=200)
    upload_url = models.CharField(max_length=200)

    def save(self, **kwargs):
        self.type = 'file_upload'
        self.ui_type = 'file'
        super(FileUploadQuestion, self).save()


class IntervalQuestion(Question):
    min_range = models.FloatField()
    max_range = models.FloatField()

    def save(self):
        self.type = 'interval_number'
        self.ui_type = 'text_number'
        super(IntervalQuestion, self).save()


class MultipleAnswerQuestion(Question):

    def save(self):
        self.type = 'multiple_answer'
        self.ui_type = 'multiple'
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


class QuestionSubmission(models.Model):
    question = models.ForeignKey(Question)
    value = models.CharField(max_length=1000, default=0)
    score = models.FloatField(default=0)
    trialSubmission = models.ForeignKey('TrialSubmission', related_name='questionSubmissions')


class TrialSubmission(models.Model):
    score = models.FloatField(default=0)
    competition = models.ForeignKey(Competition)
    trial = models.ForeignKey(Trial, null=True)
    team = models.ForeignKey(TeamParticipatesChallenge, related_name='trialSubmissions')


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
