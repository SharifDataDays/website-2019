import pytz
from django.core.management import BaseCommand, CommandError

from datetime import timedelta, datetime

from apps.accounts.models import Team
from apps.game.models import Challenge, TeamParticipatesChallenge


class Command(BaseCommand):
    help = 'Adds Max N (arg) Teams to the challenge with given id I (arg).\n' \
           'based on results of past challenge P (arg).\n' \
           'and give each team D (arg) days duration to pay the entrance_fee.\n' \
           'on second run teams with passed durations will be removed from challenge.'

    def add_arguments(self, parser):
        parser.add_argument(
            'team_count',
            type=int,
            help='max number of teams to be in challenge'
        )
        parser.add_argument(
            'challenge_id',
            type=int,
            help='challenge id to add'
        )
        parser.add_argument(
            'past_challenge_id',
            type=int,
            help='challenge id to get scores from'
        )
        parser.add_argument(
            'duration_days',
            type=int,
            help='max duration in days for teams to pay'
        )

    def handle(self, *args, **options):
        try:
            challenge = Challenge.objects.get(id=options['challenge_id'])
            past_challenge = Challenge.objects.get(id=options['past_challenge_id'])
        except Challenge.DoesNotExist:
            raise CommandError('Invalid challenge id')
        try:
            deadline = datetime.datetime.now().replace(tzinfo=pytz.UTC) + timedelta(options['duration_days'])
        except Exception:
            raise ArithmeticError('Shit datetime')

        already_participated = TeamParticipatesChallenge.objects.filter(challenge=challenge)

        for team_pc in already_participated:
            if team_pc.should_pay and not team_pc.has_paid and team_pc.payment_time_remained == 0:
                team_pc.delete()

        ranking = get_ranking(challenge=past_challenge)
        newcomers = []

        for team, i in enumerate(ranking):
            if i > challenge.invited_to_ranking:
                new_team_pc = TeamParticipatesChallenge(team=Team.objects.get(name=team['team_name']),
                                                        challenge=challenge,
                                                        payment_deadline=deadline
                                                        )
                new_team_pc.save()
                newcomers.append(new_team_pc)

                if TeamParticipatesChallenge.objects.filter(challenge=challenge).count()\
                        == options['team_count']:
                    challenge.invited_to_ranking = i
                    challenge.save()
                    break

        emails = []
        for team_pc in newcomers:
            emails.append([team_pc.team.name,
                           [(user.profile.name, user.email) for user in team_pc.team.participants],
                           ])

        emails_list = open('email.list', 'w+')
        emails_list.write('{}\n'.format(datetime.now()))
        emails_list.write('{}'.format(emails))
        emails_list.close()

        emails_csv = open('emails.csv', 'w+')
        emails_csv.write('{}\n'.format(datetime.now()))
        emails_csv.write('team_name,user_1_name,user_1_email,user_2_name,user_2_email,user_3_name,user_3_email,\n')
        for team in emails:
            emails_csv.write('{},'.format(team[0]))
            for user in team[1]:
                emails_csv.write('{},{},'.format(user[0], user[1]))
        emails_csv.close()
