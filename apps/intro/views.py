import logging
from io import BytesIO

from PIL import Image

from django.http import HttpResponseRedirect

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from django.urls import reverse


from apps.accounts.models import Team
from apps.game.models import TeamSubmission
from apps.intro.form import StaffForm
from apps.intro.models import Staff, StaffReborn, StaffTeam, StaffSubTeam

logger = logging.getLogger(__name__)


def index_2(request):
    return render(request, 'intro/index_2.html', {
        'no_sidebar': False,
        'users_count': User.objects.count(),
        'submits_count': TeamSubmission.objects.count(),
        'teams_count': Team.objects.count(),
    })

def faq(request):
    return render(request, 'intro/faq.html')


def not_found(request):
    logger.error("hello")
    logger.info("hello")
    logger.debug("hello")
    logger.warning("hello")
    return render(request, '404.html')


def staffs(request):
    staff_reborn = []
    for t in StaffTeam.objects.all():
        team = {'name': t.name,
                'sub_teams': [],
                }
        for sub_team in list(StaffSubTeam.objects.filter(parent_team=t)):
            sub = {'name': sub_team.name,
                   'members': [s for s in StaffReborn.objects.filter(sub_team=sub_team)],
                   }
            team['sub_teams'].append(sub)
        staff_reborn.append(team)

    print(staff_reborn)
    print("fuck you")
    staff = Staff.objects.all()
    return render(request, 'intro/staffs.html', {
        "staff": staff,
        "staff_reborn": staff_reborn
    })


def staff_form(request):
    form = StaffForm(request.POST, request.FILES)
    return render(request, 'intro/staff-form.html', { 'form': form } )

def add_staff(request):
    form = StaffForm(request.POST, request.FILES)
    if request.POST:
        if form.is_valid():
            image_field = form.cleaned_data['image']
            image_file = BytesIO(image_field.file.read())
            image = Image.open(image_file)
            h = image.size[1]
            w = image.size[0]
            if w < h:
                image = image.crop((0, (h - w) / 2, w, (h - w) / 2 + w)).resize((w, w), Image.ANTIALIAS)
            elif w > h:
                image = image.crop(((w - h) / 2, 0, (w - h) / 2 + h, h)).resize((h, h), Image.ANTIALIAS)
            image = image.resize((300, 300), Image.ANTIALIAS)
            image_file = BytesIO()
            image.save(image_file, 'PNG')
            image_field.file = image_file
            image_field.image = image
            for s in StaffSubTeam.objects.all():
                if s.__str__() == form.cleaned_data['team']:
                    sub_t = s
                    break
            StaffReborn.objects.create(name=form.cleaned_data['name'], sub_team=sub_t, image=image_field)
            return redirect('intro:staff')
#    return render(request, 'intro/staff-form.html', {       'form': form    })

