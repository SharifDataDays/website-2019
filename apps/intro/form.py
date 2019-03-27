from django import forms


class StaffForm(forms.Form):
    name = forms.CharField(max_length=128)
    team = forms.ChoiceField(choices=(('Technical', 'Technical'), ('Scientific', 'Scientific'),
                                      ('Branding', 'Branding'), ('Executive', 'Executive'), ('Head', 'Head')))
    image = forms.FileField()
