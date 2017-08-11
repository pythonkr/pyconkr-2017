# -*- coding: utf-8 -*-
import logging
from django.contrib import messages
from django.contrib.auth import login as user_login, logout as user_logout
from django.contrib.auth.models import User
from django.contrib.flatpages.models import FlatPage
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from datetime import datetime, timedelta
import random
from .forms import (EmailLoginForm, SpeakerForm, ProgramForm, SprintProposalForm,
                    ProposalForm, ProfileForm, TutorialProposalForm)
from .helper import sendEmailToken
from .models import (Room, Program, ProgramDate, ProgramTime, ProgramCategory,
                     Speaker, Sponsor, Announcement, Preference, TutorialProposal,
                     SprintProposal, EmailToken, Profile, Proposal, TutorialCheckin,
                     SprintCheckin)
from registration.models import Registration, Option
from constance import config

logger = logging.getLogger(__name__)
payment_logger = logging.getLogger('payment')


def index(request):
    return render(request, 'index.html', {
        'index': True,
        'base_content': FlatPage.objects.get(url='/index/').content,
        'recent_announcements': Announcement.objects.all()[:3],
    })


def schedule(request):
    dates = ProgramDate.objects.all()
    times = ProgramTime.objects.all().order_by('begin')
    rooms = Room.objects.all()

    wide = {}
    narrow = {}
    processed = set()
    for d in dates:
        wide[d] = {}
        narrow[d] = {}
        for t in times:
            if t.day_id != d.id:
                continue
            wide[d][t] = {}
            narrow[d][t] = []
            for r in rooms:
                s = Program.objects.filter(date=d, times=t, rooms=r)

                if s:
                    if s[0].times.all()[0] == t and s[0].id not in processed:
                        wide[d][t][r] = s[0]
                        narrow[d][t].append(s[0])
                        processed.add(s[0].id)
                else:
                    wide[d][t][r] = None

            if len(narrow[d][t]) == 0:
                del(narrow[d][t])

    contexts = {
        'wide': wide,
        'narrow': narrow,
        'rooms': rooms,
        'width': 100.0 / max(len(rooms), 1),
    }
    return render(request, 'schedule.html', contexts)


class RoomDetail(DetailView):
    model = Room


class SponsorList(ListView):
    model = Sponsor


class SponsorDetail(DetailView):
    model = Sponsor


class SpeakerList(ListView):
    model = Speaker


class PatronList(ListView):
    model = Registration
    template_name = "pyconkr/patron_list.html"

    def get_queryset(self):
        queryset = super(PatronList, self).get_queryset()
        patron_option = Option.objects.filter(name='PyCon-Patron')

        if patron_option:
            patron_option = patron_option.first()
            return queryset.filter(option=patron_option, payment_status='paid').order_by('-additional_price', 'created')

        return None


class SpeakerDetail(DetailView):
    model = Speaker

    def get_context_data(self, **kwargs):
        context = super(SpeakerDetail, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            if self.request.user.email == self.object.email:
                context['editable'] = True

        return context


class SpeakerUpdate(UpdateView):
    model = Speaker
    form_class = SpeakerForm

    def get_queryset(self):
        queryset = super(SpeakerUpdate, self).get_queryset()
        return queryset.filter(email=self.request.user.email)


class ProgramList(ListView):
    model = ProgramCategory
    template_name = "pyconkr/program_list.html"


class ProgramDetail(DetailView):
    model = Program

    def get_context_data(self, **kwargs):
        context = super(ProgramDetail, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            for speaker in self.object.speakers.all():
                if self.request.user.email == speaker.email:
                    context['editable'] = True

        return context


class ProgramUpdate(UpdateView):
    model = Program
    form_class = ProgramForm

    def get_queryset(self):
        queryset = super(ProgramUpdate, self).get_queryset()
        return queryset.filter(speakers__email=self.request.user.email)


class PreferenceList(SuccessMessageMixin, ListView):
    model = Preference
    template_name = "pyconkr/program_preference.html"

    def get_queryset(self):
        queryset = super(PreferenceList, self).get_queryset()
        return queryset.filter(user=self.request.user).values_list('program', flat=True)

    def post(self, request, **kwargs):
        Preference.objects.filter(user=request.user).delete()

        preferences = []
        for program_id in request.POST.getlist('program[]')[:5]:
            preferences.append(Preference(
                user=request.user,
                program=Program.objects.get(id=program_id)))

        Preference.objects.bulk_create(preferences)
        messages.success(self.request, _("Preferences are successfully updated."))
        return super(PreferenceList, self).get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PreferenceList, self).get_context_data(**kwargs)

        # Shuffle programs by user id
        programs = list(Program.objects.all())
        random.seed(self.request.user.id)
        random.shuffle(programs)

        context['programs'] = programs
        return context


class AnnouncementList(ListView):
    model = Announcement

    def get_queryset(self):
        now = datetime.now()
        queryset = super(AnnouncementList, self).get_queryset()
        return queryset.filter(Q(announce_after__isnull=True) | Q(announce_after__lt=now))


class AnnouncementDetail(DetailView):
    model = Announcement


def robots(request):
    return render(request, 'robots.txt', content_type='text/plain')


def login(request):
    if request.user.is_authenticated():
        return redirect('profile')

    form = EmailLoginForm()

    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            # Remove previous tokens
            email = form.cleaned_data['email']
            EmailToken.objects.filter(email=email).delete()

            # Create new
            token = EmailToken(email=email)
            token.save()

            sendEmailToken(request, token)
            return redirect(reverse('login_mailsent'))

    return render(request, 'login.html', {
        'form': form,
        'title': _('Login'),
    })


@never_cache
def login_req(request, token):
    time_threshold = datetime.now() - timedelta(hours=1)

    try:
        token = EmailToken.objects.get(token=token,
                                       created__gte=time_threshold)
    except ObjectDoesNotExist:
        return render(request, 'login_notvalidtoken.html',
                      {'title': _('Not valid token')})
    email = token.email

    # Create user automatically by email as id, token as password
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        user = User.objects.create_user(email, email, token)
        user.save()

    token.delete()

    # Set backend manually
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    user_login(request, user)

    return redirect(reverse('index'))


@never_cache
def login_mailsent(request):
    return render(request, 'login_mailsent.html', {
        'title': _('Mail sent'),
    })


def logout(request):
    user_logout(request)
    return redirect(reverse('index'))


class ProfileDetail(DetailView):
    model = Profile

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.profile.name:
            return redirect('profile_edit')
        return super(ProfileDetail, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, pk=self.request.user.profile.pk)

    def get_context_data(self, **kwargs):
        context = super(ProfileDetail, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            if self.request.user == self.object.user:
                context['editable'] = True
        is_registered = Registration.objects.filter(
            user=self.request.user,
            payment_status__in=['paid', 'ready']
        ).exists()
        has_proposal = Proposal.objects.filter(user=self.request.user).exists()
        has_sprint = SprintProposal.objects.filter(user=self.request.user).exists()
        has_tutorial = TutorialProposal.objects.filter(user=self.request.user).exists()
        context['is_registered'] = is_registered
        context['has_proposal'] = has_proposal
        context['has_tutorial'] = has_tutorial
        context['has_sprint'] = has_sprint
        context['title'] = _("Profile")
        return context


class ProfileUpdate(SuccessMessageMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    success_message = _("Profile successfully updated.")

    def get_queryset(self):
        queryset = super(ProfileUpdate, self).get_queryset()
        return queryset.filter(user=self.request.user)

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, pk=self.request.user.profile.pk)

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdate, self).get_context_data(**kwargs)
        context['title'] = _("Update profile")
        return context


class ProposalDetail(DetailView):
    def get_object(self, queryset=None):
        return get_object_or_404(Proposal, pk=self.request.user.proposal.pk)

    def dispatch(self, request, *args, **kwargs):
        if not Proposal.objects.filter(user=request.user).exists():
            return redirect('propose')
        return super(ProposalDetail, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProposalDetail, self).get_context_data(**kwargs)
        context['title'] = _("Proposal")
        return context


class ProposalUpdate(SuccessMessageMixin, UpdateView):
    model = Proposal
    form_class = ProposalForm
    success_message = _("Proposal successfully updated.")

    def get_object(self, queryset=None):
        return get_object_or_404(Proposal, pk=self.request.user.proposal.pk)

    def get_context_data(self, **kwargs):
        context = super(ProposalUpdate, self).get_context_data(**kwargs)
        context['title'] = _("Proposal")
        return context

    def get_success_url(self):
        return reverse('proposal')


class ProposalCreate(SuccessMessageMixin, CreateView):
    form_class = ProposalForm
    template_name = "pyconkr/proposal_form.html"
    success_message = _("Proposal successfully created.")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super(ProposalCreate, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if Proposal.objects.filter(user=request.user).exists():
            return redirect('proposal')
        if request.user.profile.name == '':
            return redirect('profile_edit')
        return super(ProposalCreate, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('proposal')


class TutorialProposalList(ListView):
    model = TutorialProposal

    def get_context_data(self, **kwargs):
        context = super(TutorialProposalList, self).get_context_data(**kwargs)
        context['tutorials'] = TutorialProposal.objects.filter(confirmed=True).all()
        context['sprints'] = SprintProposal.objects.filter(confirmed=True).all()
        if self.request.user.is_authenticated():
            proposal = TutorialProposal.objects.filter(user=self.request.user)
            sprint = SprintProposal.objects.filter(user=self.request.user)
            context['joined_tutorials'] = TutorialCheckin.objects.filter(user=self.request.user).values_list('tutorial_id', flat=True)
        return context


class TutorialProposalCreate(SuccessMessageMixin, CreateView):
    form_class = TutorialProposalForm
    template_name = "pyconkr/proposal_form.html"
    success_message = _("Tutorial proposal successfully created.")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super(TutorialProposalCreate, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        proposal = TutorialProposal.objects.filter(user=request.user)
        if proposal.exists():
            return redirect('tutorial', proposal.first().id)
        if request.user.profile.name == '':
            return redirect('profile_edit')
        return super(TutorialProposalCreate, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('tutorial', args=(self.object.id,))


class SprintProposalCreate(SuccessMessageMixin, CreateView):
    form_class = SprintProposalForm
    template_name = "pyconkr/proposal_form.html"
    success_message = _("Sprint proposal successfully created.")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super(SprintProposalCreate, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        sprint = SprintProposal.objects.filter(user=request.user)
        if sprint.exists():
            return redirect('sprint', sprint.first().id)
        if request.user.profile.name == '':
            return redirect('profile_edit')
        return super(SprintProposalCreate, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('sprint', args=(self.object.id,))


class TutorialProposalDetail(DetailView):
    model = TutorialProposal
    context_object_name = 'tutorial'

    def get_context_data(self, **kwargs):
        context = super(TutorialProposalDetail, self).get_context_data(**kwargs)
        capacity = self.object.capacity
        if capacity == 'S':
            capacity = 10
        elif capacity == 'M':
            capacity = 45
        elif capacity == 'L':
            capacity = 100
        else:
            raise Exception('invalid TutorialProposal model')
        checkin_ids = \
        TutorialCheckin.objects.filter(tutorial=self.object).\
                                order_by('id').values_list('id',flat=True)
        limit_bar_id = 65539
        if capacity < len(checkin_ids):
            limit_bar_id = checkin_ids[capacity-1]
        attendees = TutorialCheckin.objects.filter(tutorial=self.object)
        attendees = [{'name': x.user.profile.name if x.user.profile.name != '' else
                      x.user.email.split('@')[0],
                      'picture': x.user.profile.image,
                      'registered':
                      Registration.objects.filter(user=x.user,
                      payment_status='paid').exists(),
                      'waiting': True if x.id > limit_bar_id else False
                     } for x in attendees]
        context['attendees'] = attendees

        if self.request.user.is_authenticated():
            context['joined'] = \
                TutorialCheckin.objects.filter(user=self.request.user, tutorial=self.object).exists()
        else:
            context['joined'] = False

        return context


class TutorialProposalUpdate(SuccessMessageMixin, UpdateView):
    model = TutorialProposal
    form_class = TutorialProposalForm
    template_name = "pyconkr/proposal_form.html"
    success_message = _("Tutorial proposal successfully updated.")

    def get_object(self, queryset=None):
        return get_object_or_404(TutorialProposal, pk=self.request.user.tutorialproposal.pk)

    def get_context_data(self, **kwargs):
        context = super(TutorialProposalUpdate, self).get_context_data(**kwargs)
        context['title'] = _("Update tutorial")
        return context

    def get_success_url(self):
        return reverse('tutorial', args=(self.object.id,))


def tutorial_join(request, pk):
    tutorial = get_object_or_404(TutorialProposal, pk=pk)

    if request.GET.get('leave'):
        TutorialCheckin.objects.filter(user=request.user, tutorial=tutorial).delete()
    else:
        tc = TutorialCheckin(user=request.user, tutorial=tutorial)
        tc.save()

    return redirect('tutorial', pk)


class SprintProposalDetail(DetailView):
    model = SprintProposal
    context_object_name = 'sprint'

    def get_context_data(self, **kwargs):
        context = super(SprintProposalDetail, self).get_context_data(**kwargs)
        checkin_ids = \
        SprintCheckin.objects.filter(sprint=self.object).\
                                     order_by('id').values_list('id',flat=True)
        limit_bar_id = 65539
        attendees = SprintCheckin.objects.filter(sprint=self.object)
        attendees = [{'name': x.user.profile.name if x.user.profile.name != '' else
                      x.user.email.split('@')[0],
                      'picture': x.user.profile.image,
                      'registered':
                      Registration.objects.filter(user=x.user,
                      payment_status='paid').exists(),
                      'waiting': True if x.id > limit_bar_id else False
                     } for x in attendees]
        context['attendees'] = attendees

        if self.request.user.is_authenticated():
            context['joined'] = \
                SprintCheckin.objects.filter(user=self.request.user, sprint=self.object).exists()
        else:
            context['joined'] = False

        return context


class SprintProposalUpdate(SuccessMessageMixin, UpdateView):
    model = SprintProposal
    form_class = SprintProposalForm
    template_name = "pyconkr/proposal_form.html"
    success_message = _("Sprint proposal successfully updated.")

    def get_object(self, queryset=None):
        return get_object_or_404(SprintProposal, pk=self.request.user.sprintproposal.pk)

    def get_context_data(self, **kwargs):
        context = super(SprintProposalUpdate, self).get_context_data(**kwargs)
        context['title'] = _("Update sprint")
        return context

    def get_success_url(self):
        return reverse('sprint', args=(self.object.id,))


def sprint_join(request, pk):
    sprint = get_object_or_404(SprintProposal, pk=pk)

    if request.GET.get('leave'):
        SprintCheckin.objects.filter(user=request.user, sprint=sprint).delete()
    else:
        sc = SprintCheckin(user=request.user, sprint=sprint)
        sc.save()

    return redirect('sprint', pk)
