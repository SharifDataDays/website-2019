from django import forms

from apps.intro.models import StaffSubTeam

class StaffForm(forms.Form):
    
    success_url = "/staffs.html"

    name = forms.CharField(max_length=128, required=True)

    # team = forms.ChoiceField(choices=([(sub_team.__str__(), sub_team.__str__()) for sub_team in StaffSubTeam.objects.all()]),
    #         required=True)

    image = forms.FileField(required=True)
