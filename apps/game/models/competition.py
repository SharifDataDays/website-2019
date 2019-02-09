import codecs
import json

import uuid

import os
from os.path import splitext

import requests
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpResponseServerError, Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext
import datetime

from aic_site.settings.base import JUDGE_IP
from apps.game.tasks import handle_submission
from apps.accounts.models import Team
from apps.game.models.challenge import Challenge, TeamSubmission, TeamParticipatesChallenge
from django.conf import settings
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
    dataset_counter = models.IntegerField(default=0)
    trial_per_day = models.IntegerField(null=True, blank=True)
    final = models.NullBooleanField()

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
        ('file_upload', _('file_upload')), # FileUploadQuestion
        ('triple_cat_file_upload', _('triple_cat_file_upload'))
    )
    UI_TYPE_CHOICES = (
        ('text_number', _('text_number')), # single_number, interval_number
        ('text_string', _('text_string')), # single_answer, single_sufficient_answer
        ('choices', _('choices')), # multiple_choices
        ('multiple', _('multiple')), # multiple_answer
        ('file', _('file')), # file_upload
        ('image_choices', _('image_choices')) #multiple_choice
    )
    group_id = models.IntegerField(null=True, blank=True)
    doc_id = models.IntegerField(null=True, blank=True)
    stmt = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=200)
    max_score = models.FloatField(default=0, null=True)
    type = models.CharField(max_length=200, blank=True, choices=TYPE_CHOICES)
    ui_type = models.CharField(max_length=200, blank=True, choices=UI_TYPE_CHOICES)
    level = models.CharField(max_length=200, choices=LEVEL_CHOICES, blank=True, null=True)

    def __str__(self):
        # self.type = 'single_answer'
        # self.ui_type = 'text_string'
        return str('%s: %s: %s: %s' % (self.type, self.stmt, self.doc_id, self.max_score))


class MultipleChoiceQuestion(Question):

    imaged = models.BooleanField(default=False)
    #
    # def save(self):
    #     self.type = 'multiple_choice'
    #     self.ui_type = 'choices'
    #     super(MultipleChoiceQuestion, self).save()


def user_directory_path(instance, filename):
    file_extension = splitext(filename)[-1] # [1] or [-1] ?
    return str('choice_images/%d/%d%s' %(instance.question.id, instance.id, file_extension))


class Choice(models.Model):
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    text = models.CharField(max_length=200, null=True, blank=True)
    question = models.ForeignKey(MultipleChoiceQuestion, related_name='choices', null=True, blank=True)

    def save(self):
        if self.question.imaged:
            self.question.ui_type = 'image_choices'
            self.question.save()
        else:
            self.question.ui_type = 'choices'
            self.question.save()
        super(Choice, self).save()


class FileUploadQuestion(Question):
    dataset_path = models.CharField(max_length=200, null=True, blank=True)
    upload_url = models.CharField(max_length=200, null=True, blank=True)
    answer_file = models.FileField(upload_to=upload_url,null=True)
    is_chosen = models.BooleanField(default=False)

    # def save(self, **kwargs):
    #     self.type = 'file_upload'
    #     self.ui_type = 'file'
    #     super(FileUploadQuestion, self).save()


class IntervalQuestion(Question):
    min_range = models.FloatField()
    max_range = models.FloatField()

    # def save(self):
    #     self.type = 'interval_number'
    #     self.ui_type = 'text_number'
    #     super(IntervalQuestion, self).save()


class MultipleAnswerQuestion(Question):
    pass
    # def save(self):
    #     self.type = 'multiple_answer'
    #     self.ui_type = 'multiple'
    #     super(MultipleAnswerQuestion, self).save()


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
    dataset_link = models.CharField(max_length=600, blank=True, null=True)
    is_final = models.NullBooleanField()

    def save(self, *args, **kwargs):
       super(Trial, self).save()
       self.end_time = self.start_time + datetime.timedelta(hours=self.competition.trial_duration)
       super(Trial, self).save()

    def __str__(self):
        return str('%s Trial number %d' %(self.competition, self.id))

    @property
    def view_trial(self):
        if not(self.submit_time is None) or self.end_time < timezone.now():
            return False
        return True

    class Meta:
        ordering = ('-pk',)



class QuestionSubmission(models.Model):
    question = models.ForeignKey(Question)
    value = models.CharField(max_length=1000, default=0)
    score = models.FloatField(default=0)
    trial_submission = models.ForeignKey('TrialSubmission', related_name='questionSubmissions')


class TrialSubmission(models.Model):
    score = models.FloatField(default=-2)
    competition = models.ForeignKey(Competition)
    trial = models.ForeignKey(Trial, null=True)
    team = models.ForeignKey(TeamParticipatesChallenge, related_name='trial_submissions')

    def handle(self):
        if settings.TESTING:
            try:
                self.upload()
            except Exception as error:
                # logger.error(error)
                pass
        else:
            handle_submission.delay(self.id)

    def upload(self):
        context = {
            'team_id': self.team.id,
            'phase_id': self.competition.id,
            'trial_id': self.trial.id,
            'dataset_link': self.trial.dataset_link,
            'submissions': []
        }
        for q in self.trial.questions.all():
            question_context = {
                'question_id': q.doc_id,
                'question_type': q.type,
                'submitted_answer': '',
            }
            if q.type is 'file_upload':
                question_context['submitted_answer'] = q.upload_url
            else:
                try:
                    question_context['submitted_answer'] = self.questionSubmissions.get(question_id=q.id).value
                except:
                    print('empty question submitted. ignoring')
            context['submissions'].append(question_context)
        print(context)
        context['dataset_number']=12
        response = requests.post(JUDGE_IP, json=context)
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print()
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print(response.text)



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
    TYPE_CHOICES = (
        ('multiple_choice', _('multiple_choice')),  # MultipleChoiceQuestion
        ('single_answer', _('single_answer')),  # Question
        ('multiple_answer', _('multiple_answer')),  # MultipleAnswerQuestion
        ('single_sufficient_answer', _('single_sufficient_answer')),  # Question
        ('single_number', _('single_number')),  # Question type=number specified in template
        ('interval_number', _('interval_number')),  # IntervalQuestion type=number specified in template
        ('file_upload', _('file_upload'))  # FileUploadQuestion
    )
    MODEL_CHIOCES = (
        ('Question', _('Question')),
        ('IntervalQuestion', _('IntervalQuestion')),
        ('FileUploadQuestion', _('FileUploadQuestion')),
        ('MultipleAnswerQuestion', _('MultipleAnswerQuestion')),
        ('MultipleChoiceQuestion', _('MultipleChoiceQuestion')),
    )
    model_name = models.CharField(max_length=200, choices=MODEL_CHIOCES)
    type = models.CharField(max_length=200, null=True, blank=True, choices=TYPE_CHOICES)
    app = models.CharField(max_length=200)
    level = models.CharField(max_length=200, choices=CHOICES)
    number = models.IntegerField()
    phase_instruction_set = models.ForeignKey(PhaseInstructionSet)

    def __str__(self):
        return str('%s : %s' % (self.model_name , self.number))


def get_log_file_directory(instance, filename):
    return os.path.join('logs', filename + str(uuid.uuid4()))
