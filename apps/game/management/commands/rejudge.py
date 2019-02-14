import os
from sys import exit

from django.apps import apps
from django.core.management.base import BaseCommand

from apps.game.models import TrialSubmission, Competition


class Command(BaseCommand):
    help = 'Rejudges all submissions in database'

    def add_arguments(self, parser):
        parser.add_argument('phase_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        phase_id = options['phase_id'][0]
        phase = Competition.objects.get(id=phase_id)
        if phase is None:
            print('No phase with given phase_id found. exiting')
            return
        submissions = TrialSubmission.objects.filter(competition=phase)
        for s in submissions:
            s.upload()
