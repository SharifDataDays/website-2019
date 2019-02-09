import threading
import time

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from apps.accounts.models import Mail


def send(mail, rcpt, wait):
    try:
        print('waiting for {} min in background then sending {} mails'.format(wait / 60, len(rcpt)))
        time.sleep(wait)
        send_mail(subject=mail.title,
                  html_message=mail.html,
                  from_email='DataDays <datadays@sharif.edu>',
                  recipient_list=rcpt,
                  fail_silently=False
                  )
        print('successfully sent {} mails after waiting for {} min'.format(len(rcpt), wait))
    except Exception as e:
        print(e.__traceback__)


class Command(BaseCommand):
    help = 'Sends mail to all User\'s emails.'

    def add_arguments(self, parser):
        parser.add_argument(
            'mail_id',
            type=int,
            help='mail id to send'
        )
        
    def handle(self, *args, **options):
        
        mail_id = options['mail_id'][0]
        mail = Mail.objects.get(id=mail_id)
        if mail is None:
            print('NO MAIL WITH GIVEN ID FOUND')
            return
        recipients = [user.email for user in User.objects.all()]

        threads = []
        for i in range(20, len(recipients) + 20, 20):
            process = threading.Thread(target=send, args=[mail, recipients[i-20:i], int(i / 20 * 5 * 60)])
            process.start()
            threads.append(process)

        for thread in threads:
            thread.join()
