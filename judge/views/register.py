import re
from django import forms
from django.forms import CharField, ChoiceField, ModelChoiceField
from registration.backends.default.views import\
    RegistrationView as OldRegistrationView,\
    ActivationView as OldActivationView
from registration.forms import RegistrationForm
from judge.models import Profile, Language, Organization, TIMEZONE


valid_id = re.compile(r'^\w+$')


class CustomRegistrationForm(RegistrationForm):
    display_name = CharField(max_length=50, required=False, label='Real name (optional)')
    timezone = ChoiceField(choices=TIMEZONE)
    organization = ModelChoiceField(queryset=Organization.objects.all(), label='Affiliation', required=False)
    language = ModelChoiceField(queryset=Language.objects.all(), label='Default language', empty_label=None)

    def clean_username(self):
        if valid_id.match(self.cleaned_data['username']) is None:
            raise forms.ValidationError('A username must contain letters, numbers, or underscores')
        return super(CustomRegistrationForm, self).clean_username()


class RegistrationView(OldRegistrationView):
    title = 'Registration'
    form_class = CustomRegistrationForm
    template_name = 'registration/registration_form.jade'

    def get_context_data(self, **kwargs):
        if 'title' not in kwargs:
            kwargs['title'] = self.title
        return super(RegistrationView, self).get_context_data(**kwargs)

    def register(self, request, **cleaned_data):
        user = super(RegistrationView, self).register(request, **cleaned_data)
        profile, _ = Profile.objects.get_or_create(user=user, defaults={
            'language': Language.get_python2()
        })
        profile.name = cleaned_data['display_name']
        profile.timezone = cleaned_data['timezone']
        profile.language = cleaned_data['language']
        profile.organization = cleaned_data['organization']
        profile.save()
        return user

    def get_initial(self, request=None):
        initial = super(RegistrationView, self).get_initial(request)
        initial['timezone'] = 'America/Toronto'
        initial['language'] = Language.get_python2()
        return initial


class ActivationView(OldActivationView):
    title = 'Registration'
    template_name = 'registration/activate.jade'

    def get_context_data(self, **kwargs):
        if 'title' not in kwargs:
            kwargs['title'] = self.title
        return super(ActivationView, self).get_context_data(**kwargs)
