from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.forms import Textarea, EmailInput, TextInput
from django.forms.models import ModelForm
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import Profile, Mail
from apps.accounts.tokens import account_activation_token
from captcha.fields import ReCaptchaField


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    organization = forms.CharField(max_length=255, required=True)
    phone_regex = RegexValidator(regex=r'^\d{8,15}$',
                                 message=_("Please enter your phone number correctly!"))
    phone_number = forms.CharField(validators=[phone_regex], required=False)
    age = forms.IntegerField(required=False)
    captcha = ReCaptchaField()

    def is_valid(self):
        if not super().is_valid():
            return False
        if not settings.ENABLE_REGISTRATION:
            self.add_error(None, _('Registration is closed. See you next year.'))
            return False
        return True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        if commit:
            user.save()
            domain = get_current_site(self.request)
            email_text = render_to_string('email/acc_active.txt', {
                'user': user,
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })
            email_html = render_to_string('email/acc_active.html', {
                'user': user,
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })

            profile = Profile(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                organization=self.cleaned_data['organization'],
                age=self.cleaned_data['age']
            )
            profile.save()

            send_mail(subject='Activate Your Account',
                      message=email_text,
                      from_email='DataDays <datadays@sharif.edu>',
                      recipient_list=[user.email],
                      fail_silently=False,
                      html_message=email_html
                      )

        return user

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'organization', 'age', 'phone_number', 'email', 'password1',
                  'password2')


class UpdateProfileForm(ModelForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Optional.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    age = forms.IntegerField()
    password1 = forms.CharField(required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(required=False, widget=forms.PasswordInput)

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            self.add_error('password1', 'password error')

    def save(self, commit=True):
        user = super().save(commit=False)
        profile = user.profile
        profile.phone_number = self.cleaned_data['phone_number']
        profile.age = self.cleaned_data['age']
        profile.organization = self.cleaned_data['organization']

        if commit:
            user.save()
            profile.save()
        return profile

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'age', 'password1', 'password2')


class MailAdminForm(ModelForm):

    class Meta:
        model = Mail
        fields = '__all__'
        widgets = {
            'html': Textarea(),
            'from_email': EmailInput(),
            'title': TextInput()
        }


class OnSiteInformationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(OnSiteInformationForm, self).__init__(*args, **kwargs)
        self.fields['needs_residence'].help_text = ' تمایل به استفاده از اسکان مخصوص شرکت‌کننده خانم ساکن غیر تهران را دارم. <br/>'

    def is_valid(self):
        if not super(OnSiteInformationForm, self).is_valid():
            return False
        result = True
        data = self.cleaned_data
        for char in data['full_name_en']:
            if not ('a' <= char <= 'z' or 'A' <= char <= 'Z' or char in [' ', '.']):
                self.add_error('full_name_en',
                               _('English name must be fully english and contain only [a-z][A-Z][ ][.] characters.'))
                result = False
                break
        for char in data['full_name_fa']:
            if not ('\u0600' <= char <= '\u06FF' or char in [' ', '.']):
                self.add_error('full_name_fa',
                               _('Persian name must be fully Persian and contain only arabic character set plus [ ]['
                                 '.] characters.'))
                result = False
                break
        for char in data['student_id']:
            if not ('0' <= char <= '9'):
                self.add_error('student_id',
                               _('Student id must only contain [0-9].'))
                result = False
                break
        if not (1385 <= data['entrance_year'] <= 1397 or 2002 <= data['entrance_year'] <= 2019):
            self.add_error('entrance_year',
                           _('entrance year must be between [1385, 1397] or [2002, 2019]'))
            result = False
        return super().is_valid() and result

    def save(self, commit=True):
        user = super().save(commit=False)
        profile = user.profile
        profile.full_name_en = self.cleaned_data['full_name_en']
        profile.full_name_fa = self.cleaned_data['full_name_fa']
        profile.student_id = self.cleaned_data['student_id']
        profile.major = self.cleaned_data['major']
        profile.entrance_year = self.cleaned_data['entrance_year']
        profile.degree = self.cleaned_data['degree']
        profile.city = self.cleaned_data['city']
        profile.t_shirt_size = self.cleaned_data['t_shirt_size']
        profile.needs_residence = self.cleaned_data['needs_residence']
        profile.on_site_info_filled = True

        if commit:
            user.save()
            profile.save()
        return profile

    class Meta:
        model = Profile
        fields = ('full_name_en', 'full_name_fa', 'student_id', 'major', 'entrance_year', 'degree', 'city',
                  't_shirt_size', 'needs_residence')
        labels = {
            'needs_residence': 'اسکان شرکت‌کنندگان غیر مقیم در تهران به عهده خود شرکت‌کننده است. تیم برگزاری تلاش می‌کند تا اسکانی برای شرکت‌کنندگان خانم فراهم کند. در صورتی که تمایل به استفاده از این امکان دارید گزینه زیر را انتخاب کنید. هر سؤال یا ابهامی را با اکانت تلگرام @DataDays_Info یا ایمیل datadays@sharif.edu مطرح کنید.',
        }
