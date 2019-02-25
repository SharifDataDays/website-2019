from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from apps.accounts.forms.forms import UpdateProfileForm, OnSiteInformationForm
from apps.accounts.models import Profile


class UpdateProfileView(LoginRequiredMixin, generic.UpdateView):
    form_class = UpdateProfileForm
    success_url = '/accounts/panel'
    template_name = 'accounts/profile/update_profile.html'
    model = Profile

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.request.user.id)


class OnSiteInformationView(LoginRequiredMixin, generic.UpdateView):
    form_class = OnSiteInformationForm
    success_url = '/accounts/panel'
    template_name = 'accounts/profile/information.html'
    model = Profile

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.request.user.id)

    def get_form_class(self):
        form = super().get_form_class()
        form.request = self.request
        return form
