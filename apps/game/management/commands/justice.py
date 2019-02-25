import os
from sys import exit

from django.apps import apps
from django.core.management.base import BaseCommand

from apps.game.models import TrialSubmission, Competition, QuestionSubmission, TeamParticipatesChallenge

CITY_NAME_TRANSLATIONS = {
    'Tehran': 'تهران',
    'tehran': 'تهران',
    'Mashhad': 'مشهد',
    'mashhad': 'مشهد',
    'Karaj': 'کرج',
    'karaj': 'کرج',
    'Qom': 'قم',
    'qom': 'قم',
    'Isfahan': 'اصفهان',
    'isfahan': 'اصفهان',
    'Shiraz': 'شیراز',
    'shiraz': 'شیراز',
    'Tabriz': 'تبریز',
    'tabriz': 'تبریز',
    'Ahvaz': 'اهواز',
    'ahvaz': 'اهواز',
    'Kermanshah': 'کرمانشاه',
    'kermanshah': 'کرمانشاه',
}


class Command(BaseCommand):
    help = 'Brings JUSTICE back to humanity'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        teams_justified = {}

        multiple_answer_question_submissions = QuestionSubmission.objects.filter(question__type='multiple_answer')
        for submission in multiple_answer_question_submissions:

            a = submission.trial_submission.trial.score
            submission.trial_submission.trial.score -= submission.score

            submission.score = 0

            #
            submitted_answer = submission.value.strip().split('$')
            submitted_answer = [x.strip().lower() for x in submitted_answer]

            new_answers = []
            for answer in submitted_answer:
                if answer in CITY_NAME_TRANSLATIONS:
                    new_answers.append(CITY_NAME_TRANSLATIONS[answer])
                else:
                    new_answers.append(answer)

            submitted_answer = new_answers

            real_answer = submission.question.correct_answer.strip().split('$')
            real_answer = [x.strip().lower() for x in real_answer]

            correct_answer_count = len(set(real_answer).intersection(set(submitted_answer)))
            #

            submission.score = 600 * (correct_answer_count / 3)
            submission.trial_submission.trial.score += submission.score
            b = submission.trial_submission.trial.score
            if b - a != 0:
                print(b-a)
                teams_justified[submission.trial_submission.team.id] = [b - a]
            if b < a:
                print(submission.question.doc_id)
                print(submission.id)

            submission.save()
            submission.trial_submission.trial.save()

        numeric = QuestionSubmission.objects.filter(question__doc_id=151)
        for submission in numeric:
            if 750000 <= float(submission.value) <= 800000:
                submission.score = 50
                submission.trial_submission.trial.score += submission.score
                submission.save()
                submission.trial_submission.trial.save()

                if submission.trial_submission.trial.team.id in teams_justified:
                    teams_justified[submission.trial_submission.team.id].append(50)
                else:
                    teams_justified[submission.trial_submission.team.id] = [50]

        injustice_factor = 0
        for team in teams_justified:
            print("{}: {}".
                  format(TeamParticipatesChallenge.objects.get(id=team).team.name,
                         teams_justified[team]))
            injustice_factor += sum(teams_justified[team])

        print("=========")
        print("{} teams with an injustice factor of {} score".format(len(teams_justified), injustice_factor))
