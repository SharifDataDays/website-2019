import json
import math
import os
import random
from datetime import datetime
from itertools import chain
from aic_site.local_settings import PHASE_2_DATASET_PATH, PHASE_2_CATS_PATH

import pandas as pd
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import Form
from django.http import Http404, HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from aic_site.settings.base import MEDIA_ROOT
from apps.accounts.forms.panel import SubmissionForm
from apps.accounts.models import Profile
from apps.billing.decorators import payment_required
from apps.game.models import TeamSubmission, TeamParticipatesChallenge, Competition, Trial, PhaseInstructionSet, \
    Instruction, Question, \
    Choice, TrialSubmission, QuestionSubmission, FileUploadQuestion, CodeUploadQuestion
from apps.game.models.challenge import Challenge, UserAcceptsTeamInChallenge
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

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
        {'name': 'render_panel_phases_scoreboard', 'link': reverse('accounts:scoreboard'), 'text': _('Scoreboard')}
    ]

    if request.user.profile:
        if request.user.profile.panel_active_teampc:
            if request.user.profile.panel_active_teampc.should_pay and not request.user.profile.panel_active_teampc.has_paid:
                context['payment'] = request.user.profile.panel_active_teampc
            for comp in request.user.profile.panel_active_teampc.challenge.competitions.all():
                pass
                context['menu_items'].append(
                    {
                        'name': comp.name,
                        'link': reverse('accounts:panel_phase', args=[
                            comp.id
                        ]),
                        'text': _(comp.name)
                    }
                )
    context.update({
        'last_trial': Trial.objects.first()
    })

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


@login_required
def render_scoreboard(request):
    return render_phase_scoreboard(request, -1)

@login_required
def render_phase_scoreboard(request, phase_id):
    if phase_id == -1:
        scoreboard = get_scoreboard(Competition.objects.get(final=False).id)
        number_of_teams = len(scoreboard)
        for i, team in enumerate(scoreboard):
            team['scores'].append(int(team['scores'][0] * 10000 / 2350))
            team['scores'].append(int(team['scores'][1] * -1 * int(math.log((i + 1) / (number_of_teams * 2), 2))))
    else:
        scoreboard = get_scoreboard(phase_id)

    my_team = get_team_pc(request)
    context = get_shared_context(request)
    for item in context['menu_items']:
        if item['name'] == 'render_panel_phases_scoreboard':
            item['active'] = True

    page = request.GET.get('page')
    paginator = Paginator(scoreboard, 30)
    try:
        paginated_scoreboard = paginator.page(page)
    except PageNotAnInteger:
        paginated_scoreboard = paginator.page(1)
    except EmptyPage:
        paginated_scoreboard = paginator.page(paginator.num_pages)

    context.update({
        'scoreboard_links':
            [{'name': _(phase.name), 'link': reverse('accounts:phase_scoreboard', args=[phase.id])}
             for phase in Competition.objects.all()] +
            [{'name': _('Total Scoreboard'), 'link': reverse('accounts:scoreboard')}],

        'scoreboard': paginated_scoreboard,
        'my_team': my_team,
        'page_num': (paginated_scoreboard.number - 1) * 30,
    })
    if phase_id == -1:
        context.update({
            'scoreboard_name': _('Total Scoreboard'),

            'headers': [
                _('Rank'), _('Name'), _('Score'), _('Phase 1 Scaled to 10000'), _('After Formula')
            ],
        })
    else:
        context.update({
            'scoreboard_name': _(Competition.objects.get(id=phase_id).name),

            'headers': [
                _('Rank'), _('Name'), _('Score')
            ],
        })

    return render(request, 'accounts/panel/group_table.html', context)


def get_scoreboard(phase_id):
    phase = Competition.objects.get(id=phase_id)
    if phase is None:
        return redirect('accounts:panel_team_management')
    submits = TrialSubmission.objects.filter(competition=phase).select_related('trial')
    submitted_trial_ids = [submit.trial.id for submit in submits]
    trials = Trial.objects.filter(id__in=submitted_trial_ids)
    teams = TeamParticipatesChallenge.objects.filter(trials__in=trials).distinct()

    scoreboard = []
    for team in teams:
        team_con = {'team_name': team.team.name,
                    'scores': [get_phase_score(team, trials, phase)]}
        names = []
        for user_pc in team.team.participants.all():
            try:
                names.append(user_pc.user.profile.name)
            except:
                print('user has no profile')
        team_con['members'] = names
        scoreboard.append(team_con)

    scoreboard = sorted(scoreboard, key=lambda k: k['scores'][0], reverse=True)
    return scoreboard


def get_phase_score(team, trials, phase):
    team_phase_trials = trials.filter(team=team)
    if phase.final:
        try:
            return float("{0:.2f}".format(team_phase_trials.get(is_final=True).score))
        except:
            return 0
    else:
        scores = [trial.score for trial in team_phase_trials]
        if len(scores) == 0:
            result = 0
        elif len(scores) == 1:
            result = float("{0:.2f}".format(scores[0]))
        else:
            scores.remove(min(scores))
            result = float("{0:.2f}".format(sum(scores) / len(scores)))
        return result


@login_required
def render_phase(request, phase_id):
    user = request.user
    phase = Competition.objects.get(id=phase_id)
    if phase is None:
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
        current_team = None
        for team in Team.objects.all():
            for user_participation in team.participants.all():
                if user_participation.user == user:
                    current_team = team
                    break

        if len(current_team.participants.all()) == Challenge.objects.all()[0].team_size:
            is_team_completed = True
        else:
            is_team_completed = False
        trials = (Trial.objects.filter(team_id=team_pc.id, competition=phase))
        for t in trials:
            if t.submit_time is None and t.end_time <= timezone.now():
                t.submit_time = timezone.now()
                t.save()
                ts = TrialSubmission(trial=t, competition=phase, team=team_pc, score=-1)
                ts.save()
        context.update({
            'is_team_completed': is_team_completed,
            'trials': trials,
            'id': int(phase_id),
            'name': phase.name
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
    if phase.final:
        return get_new_trial_phase_2(request, phase_id)
    else:
        return get_new_trial_phase_1(request, phase_id)
        # return render_phase(request, phase_id)


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
            'id': len(Trial.objects.filter(team=team_pc, competition=phase)),
            'final': phase.final
        })
        errors = []
        if request.POST.get('file_error'):
            errors.append(request.POST['file_error'])
        if request.POST.get('code_error'):
            errors.append(request.POST['code_error'])
        if len(errors) > 0:
            context.update({
                'errors': errors
            })

        trial = Trial.objects.filter(id=trial_id).all()
        if len(trial) is 0:
            return render(request, '404.html')
        else:
            trial = trial[0]
            if trial.submit_time is None and trial.end_time <= timezone.now():
                trial.submit_time = timezone.now()
                trial.save()
                ts = TrialSubmission(trial=trial, competition=phase, team=team_pc, score=-1)
                ts.save()
            if trial.submit_time is not None:
                return redirect('accounts:panel_phase', phase_id)
            context.update({
                'phase': phase,
                'trial': trial,
                'numeric_questions': list(trial.questions.filter(type='single_number')),
                'interval_questions': list(trial.questions.filter(type='interval_number')),
                'text_questions': list(trial.questions.filter(type='single_answer')),
                'choices': list(trial.questions.filter(type='multiple_choice').order_by('max_score')),
                'multiple': list(trial.questions.filter(type='multiple_answer')),
                'file_based_questions': list(
                    trial.questions.filter(Q(type='file_upload') | Q(type='triple_cat_file_upload'))),
                'code_zip': list(trial.questions.filter(type='code_upload'))
            })

        for x in context['choices']:
            x.choices = list(Choice.objects.filter(question_id=x.id).all())
        if trial.team.id != team_pc.id:
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
            names = list(request.FILES)
            print('\033[92m{}\033[0m'.format(names))
            code = None
            if names.__contains__('code'):
                code = request.FILES['code']
                names.remove('code')
            if len(names) > 0:
                filename = names[0]
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
        if trial.team.id != team_pc.id:
            return render(request, '403.html')
        if not form.is_valid():
            return redirect('accounts:panel')
        qusu = None
        if code is not None:
            _, code_extension = os.path.splitext(code.name)
            print("-----------------------")
            print(code_extension)
            print("-----------------------")
            if code_extension.lower() not in ['.zip']:
                error_msg = 'Only zip file is acceptable'
                request.POST['code_error'] = error_msg
                return render_trial(request, phase_id, trial_id)
            elif file.size > 1048576 * 10:
                print(file.size)
                error_msg = 'Max size of csv answer is 10MB'
                request.POST['code_error'] = error_msg
                return render_trial(request, phase_id, trial_id)
            else:
                file_full_path = save_to_storage(request, 'code')
                qusu = QuestionSubmission()
                quzi = CodeUploadQuestion.objects.all()[0]
                qusu.question = quzi
                qusu.value = file_full_path
        if file is not None:
            if file.size > 1048576 * 10:

                error_msg = 'Max size of code zip is 10MB'
                request.POST['file_error'] = error_msg
                return render_trial(request, phase_id, trial_id)
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
        if trial.submit_time is not None:
            return redirect('accounts:panel_phase', phase.id)
        trial.submit_time = timezone.now()
        trial.save()
        trialSubmit = TrialSubmission()
        trialSubmit.competition = phase
        trialSubmit.team = get_team_pc(request)
        trialSubmit.trial = trial
        trialSubmit.score = -1
        trialSubmit.save()
        if qusu is not None:
            qusu.trial_submission = trialSubmit
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
            if questionSubmit.value == '':
                trial.submit_time = None
                trial.save()
                return redirect("accounts:panel_trial", phase_id, trial_id)
            questionSubmit.trial_submission = trialSubmit
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
    json_data = json.loads(request.body.decode('utf-8'))
    print('\033[92m{}\033[0m'.format(json_data))
    team_id = json_data['team_id']
    phase_id = json_data['phase_id']
    trial_id = json_data['trial_id']
    submissions = json_data['submissions']
    trial = Trial.objects.get(id=trial_id)
    trial.score = 0
    phase = Competition.objects.get(id=phase_id)
    for i in range(len(submissions)):
        question_submission = QuestionSubmission.objects.get(trial_submission__trial_id=trial_id,
                                                             question__doc_id=submissions[i]['question_id'])
        q = Question.objects.get(questionsubmission=question_submission)
        if q.type == 'triple_cat_file_upload':
            question_submission.score = submissions[i]['score'][0] * Question.objects.get(
                doc_id=submissions[i]['question_id']).max_score
            question_submission.score2 = submissions[i]['score'][1] * Question.objects.get(
                doc_id=submissions[i]['question_id']).max_score
        else:
            question_submission.score = submissions[i]['score'] * Question.objects.get(
                doc_id=submissions[i]['question_id']).max_score
        question_submission.save()
        trial.score += question_submission.score
        trial.score2 += question_submission.score2
    trial.save()

    trials = Trial.objects.filter(team_id=team_id, competition=phase)
    for t in trials:
        t.is_final = False
        t.save()
    trials = trials.order_by('-score')
    if len(trials) > 0:
        trials[0].is_final = True
        trials[0].save()
    return JsonResponse({'status': 'succeeded'})


@login_required
def get_dataset(request, phase_id, trial_id):
    phase = Competition.objects.get(id=phase_id)
    if phase is None:
        redirect("/accounts/panel/team")
    if phase.final:
        return get_dataset_2(request, phase_id, trial_id)
    else:
        return get_dataset_1(request, phase_id, trial_id)


@login_required
def get_cat(request):
    with open(PHASE_2_DATASET_PATH, 'rb') as pdf:
        response = HttpResponse(content=pdf.read(), content_type='text/csv', charset='utf8')
        response['Content-Disposition'] = 'attachment;filename=dataset.csv'
        return response


@login_required
def get_dataset_2(request, phase_id, trial_id):
    phase = Competition.objects.get(id=phase_id)
    if phase is None:
        redirect("/accounts/panel/team")
    print("\033[92mdatasetlink {}\033[0m".format(PHASE_2_DATASET_PATH))
    with open(PHASE_2_DATASET_PATH, 'rb') as pdf:
        response = HttpResponse(content=pdf.read(), content_type='text/csv', charset='utf8')
        response['Content-Disposition'] = 'attachment;filename=phase_2_dataset.csv'
        return response


def get_sample_cats(request):
    print("\033[92mdatasetlink {}\033[0m".format(PHASE_2_CATS_PATH))
    with open(PHASE_2_CATS_PATH, 'rb') as pdf:
        response = HttpResponse(content=pdf.read(), content_type='text/csv', charset='utf8')
        response['Content-Disposition'] = 'attachment;filename=phase_2_sample_answer.csv'
        return response


@login_required
def get_dataset_1(request, phase_id, trial_id):
    phase = Competition.objects.get(id=phase_id)
    if phase is None:
        redirect("/accounts/panel/team")
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
        pass
        trial = trial[0]
        if trial.submit_time is not None:
            return redirect('accounts:panel_phase', phase_id)

        question = trial.questions.get(type='file_upload')
        if question is None:
            return redirect('accounts:panel_phase', phase_id)
        link = '{}/{}.csv'.format(DIR_DATASET, question.correct_answer)
        print("\033[92mdatasetlink {}\033[0m".format(link))
        with open(link, 'rb') as pdf:
            response = HttpResponse(content=pdf.read(), content_type='text/csv', charset='utf8')
            response['Content-Disposition'] = 'attachment;filename=dataset.csv'
            return response


def get_brands(request):
    link = '/home/datadays/brands.txt'
    print("\033[92mdatasetlink {}\033[0m".format(link))
    with open(link, 'rb') as pdf:
        response = HttpResponse(content=pdf.read(), content_type='text/txt', charset='utf8')
        response['Content-Disposition'] = 'attachment;filename=brands.txt'
        return response


@login_required
def get_new_trial_phase_1(request, phase_id):
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
        trials = Trial.objects.filter(team_id=team_pc.id, competition=phase)

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
                if len(questions) == 0:
                    questions = question_model.objects.filter(trial__team=team_pc)
                questions = questions[0]
                questions.is_chosen = True
                questions.save()
                current_trial.questions.add(questions)
            else:
                if instruction.model_name == 'Question':
                    selectable_questions = question_model.objects.filter(type=instruction.type)
                else:
                    selectable_questions = question_model.objects

                if len(question_model.objects.filter(level=instruction.level).exclude(
                        trial__team=team_pc)) < instruction.number:
                    selectable_questions = selectable_questions.exclude(trial__team=team_pc)
                else:
                    selectable_questions = selectable_questions.filter(level=instruction.level).exclude(
                        trial__team=team_pc)

                questions = list(selectable_questions)
                random.shuffle(questions)
                questions = questions[:instruction.number]
                current_trial.questions.add(*questions)

        current_trial.save()
        context.update({
            'current_trial': current_trial
        })
    return redirect('accounts:panel_trial', phase_id=phase_id, trial_id=current_trial.id)


@login_required
def get_new_trial_phase_2(request, phase_id):
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
        trials = Trial.objects.filter(team_id=team_pc.id, competition=phase)

        context.update({
            'trials': trials
        })
        today_trials = 0
        for trial in trials:
            if trial.end_time > timezone.now() and trial.submit_time is None:
                context.update({
                    'error': _('You have one active trial.')
                })
                return render(request, 'accounts/panel/no_new_trial.html', context)
            if timezone.now() - trial.start_time < timezone.timedelta(hours=24):
                today_trials += 1
        print(today_trials)
        if today_trials >= phase.trial_per_day:
            context.update({
                'error': _('You can not get any new trial. You have reached your limit in current day')
            })
            return render(request, 'accounts/panel/no_new_trial.html', context)
        current_trial = Trial.objects.create(competition=phase, start_time=datetime.now(), team=team_pc)
        question = FileUploadQuestion.objects.get(type='triple_cat_file_upload')
        # todo dataset link in trial
        current_trial.questions.add(question)
        code_upload_question = CodeUploadQuestion.objects.all()[0]
        current_trial.questions.add(code_upload_question)
        current_trial.save()
        context.update({
            'current_trial': current_trial
        })
    return redirect('accounts:panel_trial', phase_id=phase_id, trial_id=current_trial.id)


@login_required
def set_final_trial(request, phase_id, trial_id):
    trial = Trial.objects.get(id=trial_id)
    if trial is None:
        return render(request, '404.html')
    phase = Competition.objects.get(id=phase_id)
    if phase is None:
        return render(request, '404.html')
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
    trials = Trial.objects.filter(team=team_pc, competition=phase)
    for t in trials:
        t.is_final = False
        t.save()
    final_trial = Trial.objects.get(id=trial_id)
    if final_trial is None:
        context.update({
            'trials': trials,
            'error': _('no such trial')
        })
    final_trial.is_final = True
    final_trial.save()
    context.update({
        'trials': trials,
        'final_trial': final_trial,
        'success': _('final trial set successfuly')
    })
    return redirect('accounts:panel_phase', phase_id=phase_id)
