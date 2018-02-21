from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.utils.translation import ugettext_lazy as _

from django.shortcuts import redirect, render

from apps.accounts.views import team_required_and_finalized
from apps.billing.forms.forms import UserCompletionForm
from apps.game.models import TeamParticipatesChallenge
from .models import Transaction


@login_required
# @team_required_and_finalized
def payment(request, participation_id):
    participation = get_object_or_404(TeamParticipatesChallenge, id=participation_id)
    if not participation.should_pay or participation.has_paid:
        return HttpResponseRedirect(reverse('accounts:panel'))
    if request.method == 'POST':
        form = UserCompletionForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            profile = form.save()
            url, t = Transaction.begin_transaction(profile=profile,
                                                   amount=participation.challenge.entrance_price,
                                                   callback_url=request.build_absolute_uri(
                                                       reverse('complete_payment')) + '?', participation=participation,
                                                   )
            if url:
                return HttpResponseRedirect(url)
            else:
                return render(request, 'billing/bank_payment_error.html', context={
                    'error': t.error,
                })
    else:
        error = None
        unverified_transaction = participation.transactions.filter(status='u')
        if unverified_transaction.exists():
            unverified_transaction.all()[0].update_status()

        if participation.transactions.filter(status='u').exists():
            error = _("You have unverified payment(s).")
        if not participation.should_pay:
            error = _("There is nothing to pay for.")
        if participation.transactions.filter(status='v').exists():
            error = _("You have already paid.")

        if error:
            return render(request, 'billing/bank_payment_error.html', context={
                'error': error,
            })
        form = UserCompletionForm(instance=request.user.profile)
        return render(request, 'billing/bank_payment.html', {
            'form': form
        })


@login_required
# @team_required_and_finalized
def complete_payment(request):
    our_id = request.GET.get('id2', None)
    if not our_id:
        raise PermissionDenied()

    transaction = get_object_or_404(Transaction, id2=our_id)
    transaction.update_status()

    if transaction.status == 'v':
        return render(request, 'billing/bank_payment_success.html')
    elif transaction.status == 'c':
        return render(request, 'billing/bank_payment_error.html', context={
            'error': transaction.error,
        })
    else:
        return redirect('payments_list')


@login_required
# @team_required_and_finalized
def payments_list(request, participation_id):
    participation = get_object_or_404(TeamParticipatesChallenge, id=participation_id)
    unknown_payments = Transaction.objects.filter(status='u')
    for transaction in unknown_payments:
        transaction.update_status()
    payments = participation.transactions.all()
    return render(request, 'billing/bank_payments_list.html', {
        'payments': payments,
    })
