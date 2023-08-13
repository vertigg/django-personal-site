from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView
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

    def get(self, request, *args, **kwargs):
        # If no new league announcements - redirect to most active league
        announcement = Announcement.get_next_announcement()
        url = self.get_redirect_url()
        if announcement or not url:
            return render(request, 'poe/main.html', {'announcement': announcement})
        return HttpResponseRedirect(url)


class PoEFilterView(FilterView):
    context_object_name = 'characters'
    model = Character
    paginate_by = 25

    def _get_current_user_profile(self, request):
        return request.user.discorduser.poe_profile if hasattr(
            request.user, 'discorduser') else None


class LadderView(PoEFilterView):
    filterset_class = PoeClassFilter
    template_name = 'poe/ladder.html'
    paginate_by = 150
    active_league = None

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


class LadderSearchView(PoEFilterView):
    filterset_class = PoeSearchFilter
    extra_context = {'title': 'Search results'}
    template_name = 'poe/search.html'
    ordering = ('name', 'level')

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().prefetch_related('gems').select_related('profile', 'league')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['current_profile'] = self._get_current_user_profile(self.request)
        return context


class StashHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'stash.html'
