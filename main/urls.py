from django.contrib.auth import views as auth_views
from main.forms import StyledAuthenticationForm
from main import views as main_views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', main_views.home, name='home'),
    url(r'^login/$', auth_views.LoginView.as_view(
        authentication_form=StyledAuthenticationForm,
        redirect_authenticated_user=True), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(
        next_page='home'), name='logout'),
    url(r'^signup/$', main_views.signup, name='signup'),
    url(r'^profile/$', main_views.profile, name='profile'),
    url(r'^unlink/$', main_views.unlink, name='unlink'),
]
