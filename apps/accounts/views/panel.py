import json
import os
import random

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.forms import Form, ModelForm
from django.http import Http404, HttpResponse, JsonResponse, FileResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from aic_site import settings
from aic_site.settings.base import MEDIA_ROOT
from apps.accounts.decorators import complete_team_required
from apps.accounts.forms.panel import SubmissionForm, ChallengeATeamForm
from apps.billing.decorators import payment_required
from apps.game.models import TeamSubmission, TeamParticipatesChallenge, Competition, Trial, PhaseInstructionSet, \
    Instruction, MultipleChoiceQuestion, FileUploadQuestion, IntervalQuestion, MultipleAnswerQuestion, Question, \
    Choice, TrialSubmission, QuestionSubmission
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime
from apps.game.models.challenge import Challenge, UserAcceptsTeamInChallenge
from django.apps import apps
from itertools import chain

DIR_DATASET = '/home/datadays/tds'


@login_required
def get_team_pc(request):
    if request.user.profile.panel_active_teampc:
        return request.user.profile.panel_active_teampc
    try:
        pc = TeamParticipatesChallenge.objects.filter(team__participants__user=request.user).order_by('-id').first()
        request.user.profile.panel_active_teampc = pc
        request.user.profile.save()
        return pc
    except TeamParticipatesChallenge.DoesNotExist:
        return None


@login_required
def get_shared_context(request):
    context = {
        'challenges': Challenge.objects.all(),
        'invitations': [],
        'accepted_participations': []
    }

    all_participations = TeamParticipatesChallenge.objects.filter(
        team__participants__user=request.user
    )
    for challenge_participation in all_participations:
        if UserAcceptsTeamInChallenge.objects.filter(team=challenge_participation, user=request.user).exists():
            context['accepted_participations'].append(challenge_participation.team)

    context['user_pcs'] = []
    for tpc in TeamParticipatesChallenge.objects.filter(team__in=context['accepted_participations']):
        context['user_pcs'].append(tpc)

    context['menu_items'] = [
        {'name': 'team_management', 'link': reverse('accounts:panel_team_management'), 'text': _('Team Status')},
        {'name': 'render_panel_phase_scoreboard', 'link': reverse('accounts:scoreboard_total'),
         'text': _('Score Board')},
    ]

    if request.user.profile:
        if request.user.profile.panel_active_teampc:
            if request.user.profile.panel_active_teampc.should_pay and not request.user.profile.panel_active_teampc.has_paid:
                context['payment'] = request.user.profile.panel_active_teampc
            for comp in request.user.profile.panel_active_teampc.challenge.competitions.all():
                context['menu_items'].append(
                    {
                        'name': comp.name,
                        'link': reverse('accounts:panel_phase', args=[
                            comp.id
                        ]),
                        'text': _(comp.name)
                    }
                )

    return context


@login_required
def change_team_pc(request, team_pc):
    try:
        new_pc = TeamParticipatesChallenge.objects.get(team__participants__user=request.user, id=team_pc)
        request.user.profile.panel_active_teampc = new_pc
        request.user.profile.save()
    except TeamParticipatesChallenge.DoesNotExist:
        raise Http404
    return redirect('accounts:panel_team_management')


@payment_required
@login_required
def submissions(request):
    team_pc = get_team_pc(request)
    if team_pc is None:
        return redirect_to_somewhere_better(request)
    context = get_shared_context(request)

    for item in context['menu_items']:
        if item['name'] == 'submissions':
            item['active'] = True

    page = request.GET.get('page', 1)
    context.update({
        'page': page,
        'participation': team_pc,
        'participation_id': team_pc.id,
    })

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid() and form.cleaned_data['team'] == team_pc:
            form.save()
            return redirect('accounts:panel_submissions')
    else:
        form = SubmissionForm()

    context['submissions'] = Paginator(
        TeamSubmission.objects.filter(team_id=team_pc.id).order_by('-id'),
        5
    ).page(page)

    if team_pc is not None:
        form.initial['team'] = team_pc
        form.fields['team'].empty_label = None
        form.fields['file'].widget.attrs['accept'] = '.zip'

    context['form'] = form
    context['team_pc'] = team_pc
    return render(request, 'accounts/panel/submissions.html', context)


def redirect_to_somewhere_better(request):
    if Challenge.objects.filter(is_submission_open=True).exists():
        return HttpResponseRedirect(
            reverse(
                'accounts:create_team',
                args=[Challenge.objects.get(is_submission_open=True).id]
            )
        )
    else:
        return HttpResponseRedirect(reverse(
            'intro:index'
        ))


def sortSecond(val):
    return val[1][0]


@login_required
def render_panel_phase_scoreboard(request):
    phase_scoreboard = TeamParticipatesChallenge.objects.filter(challenge=Challenge.objects.all()[0])
    ranks = []
    context = get_shared_context(request)
    for item in context['menu_items']:
        if item['name'] == 'render_panel_phase_scoreboard':
            item['active'] = True
    for team in phase_scoreboard:
        temp = (team.team.name, get_total_score(team.id), 0)
        ranks.append(temp)
    ranks.sort(key=sortSecond, reverse=True)
    for i in range(0, len(phase_scoreboard)):
        x = list(ranks[i])
        x[2] = i + 1
        ranks[i] = tuple(x)
    context.update({
        'teams': ranks,
        'phases': Competition.objects.all()
    })
    return render(request, 'accounts/panel/group_table.html', context)


def get_total_score(team_id):
    result = {}
    result[0] = 0
    for phase in Competition.objects.all():
        result[phase.name] = 0
        for trial in Trial.objects.filter(team=TeamParticipatesChallenge.objects.get(id=team_id), competition=phase):
            result[phase.name] += trial.score
        result[0] += result[phase.name]
    return result


@login_required
def render_phase(request, phase_id):
    user = request.user
    phase = Competition.objects.get(id=phase_id)
    if phase == None:
        redirect(reverse('accounts:panel_team_management'))
    else:
        team_pc = get_team_pc(request)
        if team_pc is None:
            return redirect_to_somewhere_better(request)
        context = get_shared_context(request)
        for item in context['menu_items']:
            if item['name'] == phase.name:
                item['active'] = True
        context.update({
            'participation': team_pc,
            'phase': phase,
        })
        from apps.accounts.models import Team
        for team in Team.objects.all():
            for user_participation in team.participants.all():
                if user_participation.user == user:
                    current_team = team
                    break
        if len(current_team.participants.all()) == Challenge.objects.all()[0].team_size:
            is_team_completed = True
        else:
            is_team_completed = False
        trials = Trial.objects.filter(team_id=team_pc.id, competition=phase)
        context.update({
            'is_team_completed': is_team_completed,
            'trials': trials
        })

    return render(request, 'accounts/panel/panel_phase.html', context)


@login_required
def team_management(request, participation_id=None):
    if participation_id is not None:
        return change_team_pc(request, participation_id)
    team_pc = get_team_pc(request)
    if team_pc is None:
        return redirect_to_somewhere_better(request)
    context = get_shared_context(request)
    for item in context['menu_items']:
        if item['name'] == 'team_management':
            item['active'] = True
    context.update({
        'participation': team_pc,
        'participation_id': team_pc.id,
        'participation_members': [
            (
                user_part.user,
                not UserAcceptsTeamInChallenge.objects.filter(
                    user=user_part.user,
                    team=team_pc
                ).exists()
            )
            for user_part in team_pc.team.participants.all()] if team_pc else [],
        'challenges': Challenge.objects.all(),
        'invitations': [],
        'accepted_participations': []
    })

    all_participations = TeamParticipatesChallenge.objects.filter(
        team__participants__user=request.user
    )
    if all_participations.count() > 0 and team_pc is None:
        return redirect('accounts:panel', all_participations.first().id)
    for challenge_participation in all_participations:
        if not UserAcceptsTeamInChallenge.objects.filter(team=challenge_participation, user=request.user).exists():
            context['invitations'].append(challenge_participation)
        else:
            context['accepted_participations'].append(challenge_participation.team)
    return render(request, 'accounts/panel/team_management.html', context)


def quest(query_set, num):
    questions = list(query_set)
    random.shuffle(questions)
    return questions[:num]


@login_required
def get_new_trial(request, phase_id):
    phase = Competition.objects.get(id=phase_id)
    if phase is None:
        redirect("/accounts/panel/team")
    else:
        team_pc = get_team_pc(request)
        if team_pc is None:
            return redirect_to_somewhere_better(request)
        context = get_shared_context(request)
        for item in context['menu_items']:
            if item['name'] == phase.name:
                item['active'] = True
        context.update({
            'participation': team_pc,
            'phase': phase,
        })
        trials = Trial.objects.filter(team_id=team_pc.id)

        context.update({
            'trials': trials
        })
        for trial in trials:
            if trial.end_time > timezone.now() and trial.submit_time is None:
                context.update({
                    'error': _('You have one active trial.')
                })
                return render(request, 'accounts/panel/no_new_trial.html', context)
        if len(trials) >= 5:
            context.update({
                'error': _('You can not get any new trial.')
            })
            return render(request, 'accounts/panel/no_new_trial.html', context)

        current_trial = Trial.objects.create(competition=phase, start_time=datetime.now(), team=team_pc)
        phase_instruction_set = PhaseInstructionSet.objects.get(phase=phase)
        instructions = Instruction.objects.filter(phase_instruction_set=phase_instruction_set)
        for instruction in instructions:
            question_model = apps.get_model(instruction.app, instruction.model_name)
            if instruction.model_name == 'FileUploadQuestion':
                questions = question_model.objects.filter(is_chosen=False).all()
                if len(questions) is 0:
                    questions = question_model.objects.filter(trial__team=team_pc)
                questions = questions[0]
                questions.is_chosen = True
                current_trial.questions.add(questions)
            else:
                selectable_questions = question_model.objects.filter(level=instruction.level).exclude(trial__team=team_pc)
                if instruction.model_name == 'Question':
                    selectable_questions = selectable_questions.filter(type=instruction.type)
                backup_questions = selectable_questions
                chosen_questions = Question.objects.filter(trial__team=team_pc)
                for q in chosen_questions:
                    selectable_questions = selectable_questions.exclude(group_id=q.group_id)
                if len(selectable_questions) < instruction.number:
                    selectable_questions = backup_questions
                questions = list(selectable_questions)
                random.shuffle(questions)
                questions = questions[:instruction.number]
                current_trial.questions.add(*questions)

        current_trial.save()
        # context.update({
        #     'current_trial': current_trial
        # })
    return redirect('accounts:panel_trial', phase_id=phase_id, trial_id=current_trial.id)


@login_required
def render_trial(request, phase_id, trial_id):
    phase = Competition.objects.get(id=phase_id)
    if phase is None:
        redirect("/accounts/panel/team")
    else:
        team_pc = get_team_pc(request)
        if team_pc is None:
            return redirect_to_somewhere_better(request)
        context = get_shared_context(request)
        for item in context['menu_items']:
            if item['name'] == phase.name:
                item['active'] = True
        context.update({
            'participation': team_pc,
            'phase': phase,
        })
        trial = Trial.objects.filter(id=trial_id).all()
        if len(trial) is 0:
            return render(request, '404.html')
        else:
            trial = trial[0]
            if trial.submit_time is not None:
                return redirect('accounts:panel_phase', phase_id)
            context.update({
                'phase': phase,
                'trial': trial,
                'numeric_questions': [x for x in list(chain(trial.questions.filter(type='single_number')
                                                            , trial.questions.filter(type='interval_number')))],
                'text_questions': [x for x in list(chain(trial.questions.filter(type='single_answer')
                                                         , trial.questions.filter(type='single_sufficient_answer')))],
                'choices': [x for x in trial.questions.filter(type='multiple_choice')],
                'multiple': [x for x in trial.questions.filter(type='multiple_answer')],
                'file_based_questions': [x for x in trial.questions.filter(type='file_upload')],
            })
        for x in context['choices']:
            x.choices = [y for y in Choice.objects.filter(question_id=x.id).all()]
        if trial.team.id is not team_pc.id:
            return render(request, '403.html')
        else:
            return render(request, 'accounts/panel/panel_trial.html', context)


@login_required
def submit_trial(request, phase_id, trial_id):
    if not request.POST:
        return redirect('accounts:panel')

    phase = Competition.objects.get(id=phase_id)

    if phase is None:
        redirect("/accounts/panel/team")
    else:
        team_pc = get_team_pc(request)
        if team_pc is None:
            return redirect_to_somewhere_better(request)
        context = get_shared_context(request)
        file = None
        if request.FILES:
            filename = list(request.FILES)[0]
            file = request.FILES[filename]
            print('\033[92m{}\033[0m'.format(file))
        for item in context['menu_items']:
            if item['name'] == phase.name:
                item['active'] = True
        context.update({
            'participation': team_pc,
            'phase': phase,
        })
        form = Form(request.POST)
        clean = {}
        for x in form.data.keys():
            if x != 'csrfmiddlewaretoken':
                clean[x] = form.data[x]
        print(clean)
        trial = Trial.objects.filter(id=trial_id).all()
        if len(trial) is 0:
            return render(request, '404.html')
        trial = trial[0]
        if not form.is_valid():
            return redirect('accounts:panel')
        qusu = None
        if file is not None:
            if file.size > 1048576:
                error_msg = 'Max size of file is 1MB'
                context.update({
                    'error': error_msg,
                })
                context.update({
                    'trial': trial,
                    'numeric_questions': [x for x in list(chain(trial.questions.filter(type='single_number')
                                                                , trial.questions.filter(type='interval_number')))],
                    'text_questions': [x for x in list(chain(trial.questions.filter(type='single_answer')
                                                             ,
                                                             trial.questions.filter(type='single_sufficient_answer')))],
                    'choices': [x for x in trial.questions.filter(type='multiple_choices')],
                    'multiple': [x for x in trial.questions.filter(type='multiple_answer')],
                    'file_based_questions': [x for x in trial.questions.filter(type='file_upload')],
                })
                for x in context['choices']:
                    x.choices = [y for y in Choice.objects.filter(question_id=x.id).all()]
                if trial.team.id is not team_pc.id:
                    return render(request, '403.html')
                else:
                    return render(request, 'accounts/panel/panel_trial.html', context)
            else:
                file_full_path = save_to_storage(request, filename)
                qusu = QuestionSubmission()
                print("aaa")
                print(filename)
                print("aaa")
                print(filename.split("_"))
                qufi = trial.questions.get(id=int(filename.split("_")[1]))
                qusu.question = qufi
                qusu.value = file_full_path
        print(clean)
        trial.submit_time = timezone.now()
        trial.save()
        trialSubmit = TrialSubmission()
        trialSubmit.competition = phase
        trialSubmit.team = get_team_pc(request)
        trialSubmit.trial = trial
        trialSubmit.save()
        if qusu is not None:
            qusu.trialSubmission = trialSubmit
            qusu.save()

        # intiated by far
        khar = {}
        for inp in clean.keys():
            print(clean[inp])
            ids = inp.split("_")
            f2ids = "_".join(ids[:2])
            if f2ids not in khar:
                khar[f2ids] = []
            khar[f2ids].append(clean[inp])

        khar = {x: '$'.join(khar[x]) for x in khar}
        print(khar)
        for x in khar.keys():
            question_id = x.split('_')[1]
            question = trial.questions.get(id=question_id)
            questionSubmit = QuestionSubmission()
            questionSubmit.question = question
            questionSubmit.value = khar[x]
            questionSubmit.trialSubmission = trialSubmit
            questionSubmit.save()

        trialSubmit.upload()
        return redirect('accounts:panel_phase', phase.id)


def save_to_storage(request, filename):
    folder = request.path.replace("/", "_")
    uploaded_filename = request.FILES[filename].name
    try:
        os.makedirs(os.path.join(MEDIA_ROOT, folder), exist_ok=True)
    except:
        pass
    full_filename = os.path.join(MEDIA_ROOT, folder, uploaded_filename)
    fout = open(full_filename, 'wb+')
    file_content = ContentFile(request.FILES[filename].read())
    for chunk in file_content.chunks():
        fout.write(chunk)
    fout.close()
    return full_filename


@csrf_exempt
def get_judge_response(request):
    print(request.body)
    json_data = json.loads(request.body.decode('utf-8'))
    print('\033[92m{}\033[0m'.format(json_data))
    team_id = json_data['team_id']
    phase_id = json_data['phase_id']
    trial_id = json_data['trial_id']
    submissions = json_data['submissions']
    trial = Trial.objects.get(id=trial_id)
    trial.score = 0
    for i in range(len(submissions)):
        trial.score += submissions[i]['score']
    trial.save()
    return JsonResponse({'status': 'succeeded'})


@login_required
def get_dataset(request, phase_id, trial_id):
    phase = Competition.objects.get(id=phase_id)
    if phase is None:
        redirect("/accounts/panel/team")
    else:
        team_pc = get_team_pc(request)
        if team_pc is None:
            return redirect_to_somewhere_better(request)
        context = get_shared_context(request)
        for item in context['menu_items']:
            if item['name'] == phase.name:
                item['active'] = True
        context.update({
            'participation': team_pc,
            'phase': phase,
        })
        trial = Trial.objects.filter(id=trial_id).all()
        if len(trial) is 0:
            return render(request, '404.html')
        else:

            trial = trial[0]
            if trial.submit_time is not None:
                return redirect('accounts:panel_phase', phase_id)
            if trial.dataset_link is None:
                i = phase.dataset_counter
                i = i + 1
                phase.dataset_counter = i
                phase.save()
                try:
                    trial.dataset_link = '{}/{}'.format(DIR_DATASET, os.listdir(DIR_DATASET)[i])
                except Exception as e:
                    phase.dataset_counter = 0
                    phase.save()
                    i = 0
                    trial.dataset_link = '{}/{}'.format(DIR_DATASET, os.listdir(DIR_DATASET)[i])
                trial.save()
            with open(trial.dataset_link, 'rb') as pdf:
                response = HttpResponse(pdf.read())
                response['content_type'] = 'text/csv'
                response['Content-Disposition'] = 'attachment;filename=dataset.csv'
                return response
