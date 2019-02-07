from django import template

from apps.game.models import TrialSubmission, QuestionSubmission
from apps.utils import jalali
import random

register = template.Library()


def isalnumdate(c):
    """
    Gets a character and returns true if char is alfanum or - or /
    """
    return c.isalnum() or c in ['-', '/']


@register.filter(name='jalali')
def georgian_to_jalali(value):
    if isinstance(value, str):
        value = ''.join(c for c in value if isalnumdate(c) or c == ' ')
        value = list(value.split())
        for part in value:
            if ':' not in part:
                value = part
                break
    return jalali.Gregorian(value).persian_string()


@register.filter
def shuffle(arg):
    tmp = list(arg)[:]
    random.shuffle(tmp)
    return tmp


@register.filter
def score(trial, arg):
    part = list(arg)[0]
    if part == '1':
        submitted_trial = TrialSubmission.objects.filter(trial=trial)
        questions = QuestionSubmission.objects.filter(trial_submission=submitted_trial)
        score = 0
        for question in questions:
            if question.question.type == 'file_upload':
                score += question.score
        return str(score)
    elif part == '2':
        submitted_trial = TrialSubmission.objects.filter(trial=trial)
        questions = QuestionSubmission.objects.filter(trial_submission=submitted_trial)
        score = 0
        for question in questions:
            if question.question.type == 'multiple_choice':
                score += question.score
        return str(score)
    elif part == '3':
        submitted_trial = TrialSubmission.objects.filter(trial=trial)
        questions = QuestionSubmission.objects.filter(trial_submission=submitted_trial)
        score = 0
        for question in questions:
            type = question.question.type
            if type != 'multiple_choice' and type != 'file_upload':
                score += question.score
        return str(score)
    else:
        return 'NaN'
