import pytz
from django.core.mail import send_mail
from django.core.management import BaseCommand, CommandError
from django.template.loader import render_to_string

from datetime import timedelta, datetime

from apps.accounts.models import Team
from apps.accounts.views import get_challenge_scoreboard
from apps.game.models import Challenge, TeamParticipatesChallenge


class Command(BaseCommand):
    help = 'Adds Max N (arg) Teams to the challenge with given id I (arg).\n' \
           'based on results of past challenge P (arg).\n' \
           'and give each team D (arg) days duration to pay the entrance_fee.\n' \
           'on second run teams with passed durations will be removed from challenge.'

    def add_arguments(self, parser):
        parser.add_argument(
            'competitors_count',
            type=int,
            help='max number of competitors to be in challenge'
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
        parser.add_argument(
            'send_mail',
            type=bool,
            help='send_mail_or_not'
        )

    def handle(self, *args, **options):
        try:
            challenge = Challenge.objects.get(id=options['challenge_id'])
            past_challenge = Challenge.objects.get(id=options['past_challenge_id'])
        except Challenge.DoesNotExist:
            raise CommandError('Invalid challenge id')
        try:
            deadline = datetime.now().replace(tzinfo=pytz.UTC) + timedelta(options['duration_days'])
        except Exception:
            raise ArithmeticError('Shit datetime')

        already_participated = TeamParticipatesChallenge.objects.filter(challenge=challenge)
        for team_pc in already_participated:
            if team_pc.should_pay and not team_pc.has_paid \
                    and team_pc.payment_deadline < datetime.now().replace(tzinfo=pytz.UTC):
                print('deleted team_pc for team {}'.format(team_pc.team.name))
                team_pc.delete()

        paid_teams_count = TeamParticipatesChallenge.objects.filter(challenge=challenge, has_paid=True).count()

        ranking = get_challenge_scoreboard(challenge_id=past_challenge.id)
        newcomers = []

        for i in range(len(ranking)):

            team = ranking[i]
            if i > challenge.invited_to_ranking \
                    and sum([len(tpc.team.participants.all())
                             for tpc in TeamParticipatesChallenge.objects.filter(challenge=challenge)]) \
                    < options['competitors_count']:
                new_team_pc = TeamParticipatesChallenge(team=Team.objects.get(name=team['team_name']),
                                                        challenge=challenge,
                                                        payment_deadline=deadline
                                                        )
                new_team_pc.save()
                newcomers.append(new_team_pc)
                print('added team_pc for team {}'.format(new_team_pc.team.name))

                challenge.invited_to_ranking = i
        challenge.save()

        print('{} new teams added\nchallenge now has {} competitors\nand {} paid teams'.format(
            len(newcomers),
            sum([len(tpc.team.participants.all())
                 for tpc in TeamParticipatesChallenge.objects.filter(challenge=challenge)]),
            paid_teams_count
        ))

        emails = []
        for team_pc in newcomers:
            emails.append([team_pc.team.name,
                           [(user_pc.user.profile.name, user_pc.user.email, user_pc.user.profile.organization)
                            for user_pc in team_pc.team.participants.all()],
                           ])

        emails_list = open('email.list', 'a')
        emails_list.write('{}\n==============================================================================\n'.format(
            datetime.now()))
        emails_list.write('{}\n'.format(emails))
        emails_list.close()
        print('emails.list file created')

        emails_csv = open('emails.csv', 'a')
        emails_csv.write('\n\n\n\n\n{}\n=====================================================================\n'.format(
            datetime.now()))
        emails_csv.write('team_name,user_1_name,user_1_email,user_2_name,user_2_email,user_3_name,user_3_email,\n')
        for team in emails:
            emails_csv.write('{},'.format(team[0]))
            for user in team[1]:
                emails_csv.write('{},{},'.format(user[0], user[1]))
            emails_csv.write('\n')
        emails_csv.close()
        print('emails.csv file created')

        commas = ""
        for team in emails:
            commas += str(team[0]) + ","
        print(commas)

        return
        # send_mails
        for team in emails:
            email_html = render_to_string('emails/invitation.html', {
                'team_name': team[0],
                'team_members': [member[0] for member in team[1]]
            })
            try:
                send_mail(subject='راهیابی به مرحله حضوری DataDays 2019',
                          message=email_html,
                          from_email='DataDays <datadays@sharif.edu>',
                          recipient_list=[member[1] for member in team[1]],
                          fail_silently=False,
                          html_message=email_html
                          )
            except Exception:
                print('sending mail for team {} failed'.format(team[0]))
