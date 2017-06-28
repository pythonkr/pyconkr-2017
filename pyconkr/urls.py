from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.flatpages import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from pyconkr.views import TutorialProposalCreate, TutorialProposalDetail, \
    TutorialProposalUpdate, TutorialProposalList, tutorial_join,\
    SprintProposalCreate, SprintProposalDetail, sprint_join, SprintProposalUpdate

from .views import index, schedule, robots
from .views import RoomDetail
from .views import AnnouncementList, AnnouncementDetail
from .views import SpeakerList, SpeakerDetail, SpeakerUpdate
from .views import SponsorList, SponsorDetail, PatronList
from .views import ProgramList, ProgramDetail, ProgramUpdate, PreferenceList
from .views import ProposalCreate, ProposalUpdate, ProposalDetail
from .views import ProfileDetail, ProfileUpdate
from .views import login, login_req, login_mailsent, logout

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^robots.txt$', robots, name='robots'),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # url(r'.*', TemplateView.as_view(template_name='teaser/index.html')),
    url(r'^$', index, name='index'),
    url(r'^room/(?P<pk>\d+)$',
        RoomDetail.as_view(), name='room'),
    url(r'^about/announcements/$',
        AnnouncementList.as_view(), name='announcements'),
    url(r'^about/announcement/(?P<pk>\d+)$',
        AnnouncementDetail.as_view(), name='announcement'),
    url(r'^about/sponsor/$',
        SponsorList.as_view(), name='sponsors'),
    url(r'^about/patron/$',
        PatronList.as_view(), name='patrons'),
    url(r'^about/sponsor/(?P<slug>\w+)$',
        SponsorDetail.as_view(), name='sponsor'),
    url(r'^programs?/list/$',
        ProgramList.as_view(), name='programs'),
    url(r'^programs?/preference/$',
        login_required(PreferenceList.as_view()), name='program_preference'),
    url(r'^program/(?P<pk>\d+)$',
        ProgramDetail.as_view(), name='program'),
    url(r'^program/(?P<pk>\d+)/edit$',
        ProgramUpdate.as_view(), name='program_edit'),
    url(r'^programs?/speakers?/$',
        SpeakerList.as_view(), name='speakers'),
    url(r'^programs?/speakers?/(?P<slug>\w+)$',
        SpeakerDetail.as_view(), name='speaker'),
    url(r'^programs?/speakers?/(?P<slug>\w+)/edit$',
        SpeakerUpdate.as_view(), name='speaker_edit'),
    url(r'^programs?/schedule/$',
        schedule, name='schedule'),
    url(r'^programs?/tutorials/$',
        TutorialProposalList.as_view(), name='tutorials'),
    url(r'^programs?/tutorial/(?P<pk>\d+)$',
        TutorialProposalDetail.as_view(), name='tutorial'),
    url(r'^programs?/tutorial/(?P<pk>\d+)/join/$',
        login_required(tutorial_join), name='tutorial-join'),
    url(r'^programs?/sprint/(?P<pk>\d+)$',
        SprintProposalDetail.as_view(), name='sprint'),
    url(r'^programs?/sprint/(?P<pk>\d+)/join/$',
        login_required(sprint_join), name='sprint-join'),
    url(r'^cfp/propose/$',
        login_required(ProposalCreate.as_view()), name='propose'),
    url(r'^cfp/tutorial-propose/$',
        login_required(TutorialProposalCreate.as_view()), name='tutorial-propose'),
    url(r'^profile/proposal/$',
        login_required(ProposalDetail.as_view()), name='proposal'),
    url(r'^cfp/sprint-propose/$',
        login_required(SprintProposalCreate.as_view()), name='sprint-propose'),
    url(r'^profile/proposal/edit$',
        login_required(ProposalUpdate.as_view()), name='proposal-update'),
    url(r'^profile/tutorial-proposal/edit$',
        login_required(TutorialProposalUpdate.as_view()), name='tutorial-proposal-update'),
    url(r'^profile/sprint-proposal/edit$',
        login_required(SprintProposalUpdate.as_view()), name='sprint-proposal-update'),
    url(r'^profile$',
        login_required(ProfileDetail.as_view()), name='profile'),
    url(r'^profile/edit$',
        login_required(ProfileUpdate.as_view()), name='profile_edit'),

    url(r'^login/$', login, name='login'),
    url(r'^login/req/(?P<token>[a-z0-9\-]+)$', login_req, name='login_req'),
    url(r'^login/mailsent/$', login_mailsent, name='login_mailsent'),
    url(r'^logout/$', logout, name='logout'),

    url(r'^registration/', include('registration.urls')),

    # for flatpages
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^(?P<url>.*/)$', views.flatpage, name='flatpage'),

    prefix_default_language=False
)

# for development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# for rosetta
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^rosetta/', include('rosetta.urls')),
    ]
