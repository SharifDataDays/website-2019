import os
from sys import exit

from django.apps import apps
from django.core.management.base import BaseCommand

from apps.game.models import TrialSubmission


class Command(BaseCommand):
    help = 'Rejudges all submissions in database'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        submissions = TrialSubmission.objects.all()
        for s in submissions:
            s.upload()