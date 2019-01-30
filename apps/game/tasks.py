from celery import shared_task

import logging

logger = logging.getLogger(__name__)


@shared_task
def handle_submission(submission_id):
    from apps.game.models import TrialSubmission
    submission = TrialSubmission.objects.get(id=submission_id)
    try:
        submission.upload()
    except Exception as error:
        pass
        # logger.error(error)
