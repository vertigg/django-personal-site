from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import TemplateView
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import RedirectView
from django_filters.views import FilterView

from poe.filters import PoeClassFilter, PoeSearchFilter
from poe.models import Announcement, Character, League


class MainLadderView(RedirectView):
    """Returns main page or current most populated league ladder"""

    def get_redirect_url(self):
        top_league = (
            League.objects
            .filter(character__isnull=False)
            .distinct()
            .filter(end_date__gt=timezone.localtime())
            .annotate(players=Count('character'))
            .order_by('-players')
            .first()
        )
        if top_league:
            return reverse('poe:ladder_url', kwargs={'slug': top_league.slug})
        return None

    def get_context(self) -> Dict[str, Any]:
        return {
            'ladder_main': True,
            'announcement': Announcement.get_next_announcement(),
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context()
        # If no new league announcements - proceed to most active current league
        url = self.get_redirect_url()
        if context.get('announcement') or not url:
            return render(request, 'ladder.html', context)
        return HttpResponseRedirect(url)


class LadderView(FilterView):
    filterset_class = PoeClassFilter
    context_object_name = 'characters'
    template_name = 'ladder.html'
    model = Character
    paginate_by = 150
    active_league = None

    def _get_current_user_profile(self, request):
        return request.user.discorduser.poe_profile if hasattr(
            request.user, 'discorduser') else None

    def get_queryset(self):
        self.active_league = get_object_or_404(League, slug=self.kwargs.get('slug'))
        return (
            Character.objects
            .filter(league_id=self.active_league.id)
            .order_by('-level', '-experience')
            .prefetch_related('gems')
            .select_related('profile')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_league'] = self.active_league
        context['class_filter'] = self.filterset_class(self.request.GET, context.get('characters'))
        context['current_profile'] = self._get_current_user_profile(self.request)
        return context


class LadderSearchView(FilterView):
    extra_context = {'search': True, 'title': 'Search results'}
    context_object_name = 'search_results'
    filterset_class = PoeSearchFilter
    template_name = 'ladder.html'
    model = Character
    paginate_by = 10
    ordering = 'name'


class StashHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'stash.html'
