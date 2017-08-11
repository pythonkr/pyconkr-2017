from collections import OrderedDict

from django.utils import timezone
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from .models import SponsorLevel, Speaker, Banner


def default(request):
    title = None
    # remove i18n_patterns prefix for flatpage
    url = request.path.replace('/' + request.LANGUAGE_CODE, '')
    if settings.FORCE_SCRIPT_NAME:
        url = url[len(settings.FORCE_SCRIPT_NAME):]
    base_content = FlatPage.objects.filter(url=url).first()

    submenu = None
    menu = OrderedDict([
        ('about', {
            'title': _('About'),
            'icon': 'python',
            'submenu': OrderedDict([
                ('pyconkr', {'title': _('About PyCon Korea 2017')}),
                ('coc', {'title': _('Code of Conduct')}),
                ('blog', {'title': _('PyCon.KR 2017 Blog')}),
                ('announcements', {'title': _('Announcements')}),
                ('sponsor', {'title': _('Sponsors')}),
                ('patron', {'title': _('Patrons')}),
                ('sponsorship', {'title': _('Sponsorship')}),
                ('staff', {'title': _('Staff')}),
                ('contact', {'title': _('Contact')}),
            ]),
        }),
        ('program', {
            'title': _('Programs'),
            'icon': 'calendar',
            'submenu': OrderedDict([
                ('schedule', {'title': _('Schedule')}),
                ('list', {'title': _('Program list')}),
                ('keynote', {'title': _('Keynotes')}),
                ('speaker', {'title': _('Speakers')}),
                ('tutorials', {'title': _('Sprint and Tutorial')}),
                ('young_coder', {'title': _('Young Coder')}),
                ('child_care', {'title': _('Child Care')}),
                ('lightning_talk', {'title': _('Lightning talk')}),
                ('ost', {'title': _('Open Spaces')}),
            ]),
        }),
        ('venue', {
            'title': _('Venue'),
            'icon': 'map-marker',
            'submenu': OrderedDict([
                ('map', {'title': _('Venue Map')}),
                ('transportation', {'title': _('Transportation')}),
            ]),
        }),
        ('cfp', {
            'title': _('Proposal'),
            'icon': 'edit',
            'submenu': OrderedDict([
                ('cfp', {'title': _('Call for proposals')}),
                ('howto', {'title': _('How to propose')}),
            ]),
        }),
        ('registration', {
            'title': _('Registration'),
            'icon': 'book',
            'submenu': OrderedDict([
                ('information', {'title': _('Information')}),
                ('purchase', {'title': _('Purchase a ticket')}),
                ('finacial-aid', {'title': _('Financial Aid')}),
            ]),
        }),
    ])

    rp = request.path[len(settings.FORCE_SCRIPT_NAME):]

    for k, v in menu.items():
        path = '/{}/'.format(k)

        if rp.startswith(path):
            v['active'] = True
            title = v['title']

            if 'submenu' in v:
                submenu = v['submenu']

                for sk, sv in v['submenu'].items():
                    sv['path'] = '{}{}/'.format(path, sk)
                    subpath = sv['path']

                    if rp == subpath:
                        sv['active'] = True
                        title = sv['title']

    now = timezone.now()
    banners = Banner.objects.filter(begin__lte=now, end__gte=now)

    c = {
        'menu': menu,
        'submenu': submenu,
        'banners': banners,
        'title': title,
        'domain': settings.DOMAIN,
        'base_content': base_content.content if base_content else '',
    }
    return c


def profile(request):
    speaker = None
    programs = None

    if request.user.is_authenticated():
        speaker = Speaker.objects.filter(email=request.user.email).first()
        if speaker:
            programs = speaker.program_set.all()

    return {
        'my_speaker': speaker,
        'my_programs': programs,
    }


def sponsors(request):
    levels = SponsorLevel.objects.annotate(
        num_sponsors=Count('sponsor')).filter(num_sponsors__gt=0)

    return {
        'levels': levels,
    }
