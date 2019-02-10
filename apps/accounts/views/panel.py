import json
import os
import random
from datetime import datetime
from itertools import chain

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
        {'name': 'render_panel_phases_scoreboard', 'link': reverse('accounts:scoreboard_total'), 'text': _('Scoreboard')}
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
                context['menu_items'].append(
                    {
                        'name': comp.name+" scoreboard",
                        'link': reverse('accounts:phase_scoreboard', args=[
                            comp.id
                        ]),
                        'text': _(comp.name+" scoreboard")
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


def sortSecond(val):
    return val[1][0]


@login_required
def render_panel_phases_scoreboard(request):
    # phase_scoreboard = TeamParticipatesChallenge.objects.filter(challenge=Challenge.objects.all()[0])
    submissions = TrialSubmission.objects.filter(competition__challenge=Challenge.objects.all()[0])
    scoreboard = TeamParticipatesChallenge.objects.filter(trial_submissions__in=list(submissions)).distinct()
    ranks = []
    context = get_shared_context(request)
    for item in context['menu_items']:
        if item['name'] == 'render_panel_phase_scoreboard':
            item['active'] = True
    for team in scoreboard:
        profiles = Profile.objects.filter(panel_active_teampc=team)
        members = []
        for prof in profiles:
            members.append(prof.user)
        temp = (team.team.name, get_total_score(team.id), 0, Profile.objects.filter(panel_active_teampc=team))
        ranks.append(temp)
    ranks.sort(key=sortSecond, reverse=True)
    for i in range(0, len(scoreboard)):
        x = list(ranks[i])
        x[2] = i + 1
        ranks[i] = tuple(x)
    my_team = get_team_pc(request).team.name
    context.update({
        'teams': ranks,
        'phases': Competition.objects.all(),
        'my_team': my_team,
    })
    return render(request, 'accounts/panel/group_table.html', context)


def get_total_score(team_id):
    result = {0: 0}
    for phase in Competition.objects.all():
        result[phase.name] = 0
        trials = Trial.objects.filter(team=TeamParticipatesChallenge.objects.get(id=team_id), competition=phase).all()
        scores = []
        for trial in trials:
            scores.append(trial.score)
        if len(scores) == 0:
            result[phase.name] = 0
        elif len(scores) == 1:
            result[phase.name] = float("{0:.2f}".format(scores[0]))
        else:
            scores.remove(min(scores))
            result[phase.name] = float("{0:.2f}".format(sum(scores) / len(scores)))
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
        context.update({
            'is_team_completed': is_team_completed,
            'trials': trials,
        })

    return render(request, 'accounts/panel/panel_phase.html', context)


@login_required
def render_phase_scoreboard(request,phase_id):
    phase = Competition.objects.get(id=phase_id)
    phase_scoreboard = TeamParticipatesChallenge.objects.filter()
    ranks = []
    context = get_shared_context(request)
    for item in context['menu_items']:
        if item['name'] == phase.name+' scoreboard':
            item['active'] = True
    for team in phase_scoreboard:
        temp = [team.team.name, get_score(team.id,phase), 0,Profile.objects.filter(panel_active_teampc=team),True]
        if len(Trial.objects.filter(team=TeamParticipatesChallenge.objects.get(id=team.id), competition=phase)) == 0:
            temp[4] = False
        ranks.append(temp)
    ranks.sort(key=sortPhase, reverse=True)
    for i in range(0, len(phase_scoreboard)):
        x = list(ranks[i])
        x[2] = i + 1
        ranks[i] = (x)
    context.update({
        'teams': ranks,
        'phase':phase
    })
    return render(request, 'accounts/panel/phase_table.html', context)


def sortPhase(val):
    return val[1]

def get_score(team_id,phase):
    result = 0
    list = []
    if phase.final == True:
        list.append(Trial.objects.get(is_final=True).score)
    else:
        for trial in Trial.objects.filter(team=TeamParticipatesChallenge.objects.get(id=team_id), competition=phase):
            list.append(trial.score)
        if len(Trial.objects.filter(team=TeamParticipatesChallenge.objects.get(id=team_id), competition=phase))>1:
            list.remove(min(list))
    for i in list:
        result+=i
    if phase.final == False and len(list)!=0:
        result = int(result/len(list))
    return result



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

@login_required
def render_trial(request, phase_id, trial_id):
    phase = Competition.objects.get(id=phase_id)
    if request.POST.get('file_error'):
        print(request.POST['file_error'])
    if request.POST.get('code_error'):
        print(request.POST['code_error'])
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
                'numeric_questions': list(trial.questions.filter(type='single_number')),
                'interval_questions': list(trial.questions.filter(type='interval_number')),
                'text_questions': list(trial.questions.filter(type='single_answer')),
                'choices': list(trial.questions.filter(type='multiple_choice').order_by('max_score')),
                'multiple': list(trial.questions.filter(type='multiple_answer')),
                'file_based_questions': list(trial.questions.filter(Q(type='file_upload')|Q(type='triple_cat_file_upload'))),
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
            if code_extension not in ['.zip']:
                error_msg = 'Only zip file is acceptable'
                request.POST['code_error'] = error_msg
                return render_trial(request, phase_id, trial_id)
            elif file.size > 1048576:
                error_msg = 'Max size of file is 1MB'
                request.POST['code_error'] = error_msg
                return render_trial(request, phase_id, trial_id)
            else:
                file_full_path = save_to_storage(request, 'code')
                qusu = QuestionSubmission()
                quzi = CodeUploadQuestion.objects.all()[0]
                qusu.question = quzi
                qusu.value = file_full_path
        if file is not None:
            if file.size > 1048576:
                error_msg = 'Max size of file is 1MB'
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
    for i in range(len(submissions)):
        question_submission = QuestionSubmission.objects.get(trial_submission__trial_id=trial_id, question__doc_id=submissions[i]['question_id'])
        question_submission.score = submissions[i]['score'] * Question.objects.get(doc_id=submissions[i]['question_id']).max_score
        question_submission.save()
        trial.score += question_submission.score
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
def get_new_trial_phase_1(request, phase_id)
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
        trials = Trial.objects.filter(team_id=team_pc.id)

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
            if timezone.now()-trial.start_time < timezone.timedelta(hours=24):
                today_trials += 1
        print(today_trials)
        if today_trials >= phase.trial_per_day:
            context.update({
                'error': _('You can not get any new trial. You have reached your limit in current day')
            })
            return render(request, 'accounts/panel/no_new_trial.html', context)
        current_trial = Trial.objects.create(competition=phase, start_time=datetime.now(), team=team_pc)
        question = FileUploadQuestion.objects.get(type='triple_cat_file_upload')
        #todo dataset link in trial
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
