from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from wowstats.models import WOWAccount, WOWStatSnapshot, WOWCharacter
from wowstats.oauth2 import BlizzardAPI
from subprocess import Popen
from django.urls import reverse
from wowstats.forms import RegionChoiceForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseForbidden
import json
client = BlizzardAPI()


def track(request):
    id = request.POST.get('id', None)
    state = json.loads(request.POST.get('track', 'null'))
    if state is not None:
        w = WOWCharacter.objects.get(id=id)
        w.track = state
        w.save()
        return JsonResponse({'status': 201})
    else:
        return HttpResponseForbidden()


class CharacterView(DetailView):
    model = WOWCharacter
    template_name = 'character_detail.html'

    def get_object(self):
        realm = self.kwargs.get('realm', None)
        name = self.kwargs.get('name', None)
        character = get_object_or_404(WOWCharacter, realm=realm, name=name)
        return character


class MainView(LoginRequiredMixin, FormView):
    login_url = '/login/'
    template_name = 'wow_main.html'
    form_class = RegionChoiceForm
    success_url = '.'

    def token_expired(self, profile):
        expires_in = profile.wowaccount.register_date + timedelta(days=25)
        return True if now() > expires_in else False

    def build_authorization_url(self, region):
        state = self.request.META['HTTP_COOKIE'].split(';')[0].split('=')[1]
        client.site = client.template.format(region)
        authorization_url = client.authorize_url(
            scope='wow.profile',
            response_type="code",
            state=state,
            region=region)
        return authorization_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        profile = (User.objects
                   .select_related('wowaccount')
                   .select_related('wowsettings')
                   .get(pk=self.request.user.pk))
        context['profile'] = profile
        context['authorized'] = True if hasattr(
            profile, 'wowaccount') else False
        if context['authorized']:
            context['token_update'] = self.token_expired(profile)
            context['characters'] = (profile.wowaccount
                                     .wowcharacter_set.all()
                                     .filter(is_pvp=True)
                                     .order_by('-last_modified'))
            paginator = Paginator(context['characters'], 7)
            try:
                characters_pg = paginator.page(page)
            except PageNotAnInteger:
                characters_pg = paginator.page(1)
            except EmptyPage:
                characters_pg = paginator.page(paginator.num_pages)
            context['characters_pg'] = characters_pg
        context['success'] = self.request.GET.get('success', None)
        return context

    def form_valid(self, form):
        if self.request.POST.get('region', None):
            region = self.request.POST.get('region')
        else:
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
        if data.get('access_token', None):
            auth_token = data['access_token']
            # Debug
            # p = Popen("python manage.py wowstats_update --id {0} --token {1} --region {2}"
            #           .format(request.user.id, auth_token, region))
            p = Popen("cd /home/vertigo/homesite/ && /home/vertigo/env/bin/python3 /home/vertigo/homesite/manage.py wowstats_update --id {0} --token {1} --region {2}"
                      .format(request.user.id, auth_token, region), shell=True)
            return redirect(reverse('wowstats:main') + '?success=true')
        else:
            return redirect(reverse('wowstats:main') + '?success=false')
    except Exception as ex:
        print(ex)
        return redirect(reverse('wowstats:main') + '?success=false')
