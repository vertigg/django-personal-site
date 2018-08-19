from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from wowstats.models import WOWAccount
from wowstats.oauth2 import BlizzardAPI
from django.core.management import call_command
from django.http import JsonResponse
from subprocess import Popen
from django.urls import reverse
from wowstats.forms import RegionChoiceForm
from django.contrib.auth.mixins import LoginRequiredMixin

client = BlizzardAPI()


class MainView(LoginRequiredMixin, FormView):
    login_url = '/login/'
    template_name = 'wow_main.html'
    form_class = RegionChoiceForm
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = (User.objects
                   .select_related('wowaccount')
                   .select_related('wowsettings')
                   .get(pk=self.request.user.pk))
        context['profile'] = profile
        context['authorized'] = True if hasattr(
            profile, 'wowaccount') else False
        if context['authorized']:
            context['characters'] = (profile.wowaccount
                                     .wowcharacter_set.all()
                                     .order_by('-level'))
        context['success'] = self.request.GET.get('success', None)
        return context

    def build_authorization_url(self, region):
        state = self.request.META['HTTP_COOKIE'].split(';')[0].split('=')[1]
        client.site = client.template.format(region)
        authorization_url = client.authorize_url(
            scope='wow.profile',
            response_type="code",
            state=state,
            region=region)
        return authorization_url

    def form_valid(self, form):
        region = form.cleaned_data.get('name', 'eu')
        self.request.session['region'] = region
        url = self.build_authorization_url(region)
        return redirect(url)


def _callback(request):
    region = request.session.get('region', 'eu')
    state = request.GET.get('state', None)
    code = request.GET.get('code', None)
    try:
        data = client.get_token(code=code, state=state,
                                grant_type="authorization_code")
        print(data)
        if data.get('access_token', None):
            auth_token = data['access_token']
            p = Popen("python manage.py wowstats_update --id {0} --token {1} --region {2}"
                      .format(request.user.id, auth_token, region))
            return redirect(reverse('wowstats:main') + '?success=True')
        else:
            return redirect(reverse('wowstats:main') + '?success=False')
    except Exception as ex:
        print(ex)
        return redirect(reverse('wowstats:main') + '?success=False')
