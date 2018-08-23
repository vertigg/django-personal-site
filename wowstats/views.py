import json
from datetime import timedelta
from subprocess import Popen

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseForbidden, JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.timezone import now
from datetime import timedelta
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

from wowstats.forms import RegionChoiceForm
from wowstats.models import WOWCharacter, WOWStatSnapshot, PVPBracket
from wowstats.oauth2 import BlizzardAPI

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest"] = (WOWStatSnapshot.objects
                             .filter(character_id=self.object.id)
                             .select_related('arena_2v2', 'arena_3v3', 'arena_rbg')
                             .latest())
        context["previous"] = (WOWStatSnapshot.objects
                               .filter(character_id=self.object.id, snapshot_date__lt=context['latest'].snapshot_date)
                               .select_related('arena_2v2', 'arena_3v3', 'arena_rbg')
                               .first())
        return context

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


def get_month_stats(request):
    """Returns 30 day statistics for character_id"""
    char_id = int(request.GET.get('character', 0))
    delta = now() - timedelta(days=30)
    if not WOWCharacter.objects.filter(id=char_id).exists():
        raise Http404("Character not found")
    chart_stats = (WOWStatSnapshot.objects
                   .filter(character_id=char_id)
                   .filter(snapshot_date__lte=now(), snapshot_date__gte=delta)
                   .select_related('arena_2v2', 'arena_3v3', 'arena_rbg')
                   .values('snapshot_date', 'arena_2v2__rating', 'arena_3v3__rating', 'arena_rbg__rating')
                   .order_by('-snapshot_date'))
    data = json.dumps([{'date': x['snapshot_date'].strftime("%Y-%m-%d"),
                        '2v2': x['arena_2v2__rating'],
                        '3v3': x['arena_3v3__rating'],
                        'rbg': x['arena_rbg__rating']}
                       for x in chart_stats])
    return JsonResponse(data, safe=False)
