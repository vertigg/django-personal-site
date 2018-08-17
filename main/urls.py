from django.contrib.auth import views as auth_views
from main.forms import StyledAuthenticationForm
from main.views import home_view, signup, profile, unlink
from django.conf.urls import url

urlpatterns = [
    url(r'^$', home_view, name='home'),
    url(r'^login/$', auth_views.login,
        {'authentication_form': StyledAuthenticationForm, 'redirect_authenticated_user': True}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'home'}, name='logout'),
    url(r'^signup/$', signup, name='signup'),
    url(r'^profile/$', profile, name='profile'),
    url(r'^unlink/$', unlink, name='unlink'),
]
