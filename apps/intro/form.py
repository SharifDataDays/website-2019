from django import forms


class StaffForm(forms.Form):
    name = forms.CharField(max_length=128, required=False)
    team = forms.ChoiceField(choices=(('Technical', 'Technical'), ('Scientific', 'Scientific'),
                                      ('Branding', 'Branding'), ('Executive', 'Executive'), ('Head', 'Head')), required=False)
    image = forms.FileField(required=False)
