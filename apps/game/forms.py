from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.forms.models import ModelForm
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from apps.accounts.models import Profile
from apps.accounts.tokens import account_activation_token
from captcha.fields import ReCaptchaField

