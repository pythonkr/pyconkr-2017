# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import date as _date
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail import ImageField as SorlImageField
from jsonfield import JSONField
from uuid import uuid4
from constance import config

class Room(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, null=True, blank=True)
    desc = models.TextField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('room', args=[self.id])

    def __str__(self):
        return self.name


class ProgramDate(models.Model):
    day = models.DateField()

    def __str__(self):
        return _date(self.day, "Y-m-d (D)")


class ProgramTime(models.Model):
    name = models.CharField(max_length=100)
    begin = models.TimeField()
    end = models.TimeField()
    day = models.ForeignKey(ProgramDate, null=True, blank=True)

    def __meta__(self):
        ordering = ['begin']

    def __str__(self):
        return '%s - %s / %s / %s' % (self.begin, self.end, self.name, self.day)


class ProgramCategory(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)

    show_in_mobile = models.BooleanField(default=True)
    show_in_list = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SponsorLevelManager(models.Manager):
    def get_queryset(self):
        return super(SponsorLevelManager, self).get_queryset().all().order_by('order')


class SponsorLevel(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    desc = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=1)

    objects = SponsorLevelManager()

    def __str__(self):
        return self.name


class Sponsor(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100, db_index=True)
    image = models.ImageField(upload_to='sponsor', null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    level = models.ForeignKey(SponsorLevel, null=True, blank=True)

    class Meta:
        ordering = ['id']

    def get_absolute_url(self):
        return reverse('sponsor', args=[self.slug])

    def __str__(self):
        return self.name


class Speaker(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100, db_index=True)
    organization = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=255, db_index=True,
                              null=True, blank=True)
    image = models.ImageField(upload_to='speaker', null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    info = JSONField(blank=True, help_text=_('help-text-for-speaker-info'))

    class Meta:
        ordering = ['name']

    def get_badges(self, size_class=""):
        badge = \
            '<a class="btn btn-social btn-social-default {} btn-{}" href="{}" target="_blank">' \
            '<i class="fa fa-external-link fa-{}"></i>{}</a>'
        fa_replacement = {
            "homepage": "home",
            "blog": "pencil",
        }
        result = []
        if type(self.info) == str:
            return '<div class="badges">{}</div>'.format(' '.join(result))
        
        for site, url in self.info.items():
            result.append(badge.format(
                size_class,
                site, url,
                fa_replacement.get(site, site), site.capitalize()
            ))
        return '<div class="badges">{}</div>'.format(' '.join(result))

    def get_badges_xs(self):
        return self.get_badges("btn-xs")

    def get_absolute_url(self):
        return reverse('speaker', args=[self.slug])

    def get_image_url(self):
        if self.image:
            return self.image.url

        return static('image/anonymous.png')

    def __str__(self):
        return '%s / %s' % (self.name, self.slug)


class Program(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    brief = models.TextField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    slide_url = models.CharField(max_length=255, null=True, blank=True)
    pdf_url = models.CharField(max_length=255, null=True, blank=True)
    video_url = models.CharField(max_length=255, null=True, blank=True)
    speakers = models.ManyToManyField(Speaker, blank=True)
    difficulty = models.CharField(max_length=1,
                                  choices=(
                                      ('B', _('Beginner')),
                                      ('I', _('Intermediate')),
                                      ('E', _('Experienced')),
                                  ), default='B')

    duration = models.CharField(max_length=1,
                                choices=(
                                    ('S', _('25 mins')),
                                    ('L', _('40 mins')),
                                ), default='S')

    language = models.CharField(max_length=1,
                                choices=(
                                    ('E', _('English')),
                                    ('K', _('Korean')),
                                ), default='E')

    date = models.ForeignKey(ProgramDate, null=True, blank=True)
    rooms = models.ManyToManyField(Room, blank=True)
    times = models.ManyToManyField(ProgramTime, blank=True)
    category = models.ForeignKey(ProgramCategory, null=True, blank=True)

    is_recordable = models.BooleanField(default=True)
    is_breaktime = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('program', args=[self.id])

    def room(self):
        rooms = self.rooms.all()

        if rooms.count() == Room.objects.all().count():
            return ''

        return ', '.join([_.name for _ in self.rooms.all()])

    def get_slide_url_by_begin_time(self):
        from datetime import datetime

        if not config.SHOW_SLIDE_DATA:
            return None

        time = self.times.first()

        if not time:
            return None

        if datetime.now().date() > time.day.day and datetime.now().time() > time.begin:
            return self.slide_url
        else:
            return None

    def begin_time(self):
        return self.times.all()[0].begin.strftime("%H:%M")

    def get_speakers(self):
        return ', '.join([u'{}({})'.format(_.name, _.email) for _ in self.speakers.all()])
    get_speakers.short_description = u'Speakers'

    def get_times(self):
        times = self.times.all()

        if times:
            return '%s - %s' % (times[0].begin.strftime("%H:%M"),
                                times[len(times) - 1].end.strftime("%H:%M"))
        else:
            return _("Not arranged yet")

    def __str__(self):
        return self.name


class Announcement(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    desc = models.TextField(null=True, blank=True)

    announce_after = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def at(self):
        return self.announce_after if self.announce_after else self.created

    def __str__(self):
        return self.title


class EmailToken(models.Model):
    email = models.EmailField(max_length=255)
    token = models.CharField(max_length=64, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.token = str(uuid4())
        super(EmailToken, self).save(*args, **kwargs)


class Proposal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    brief = models.TextField(max_length=1000)
    desc = models.TextField(max_length=4000)
    comment = models.TextField(max_length=4000, null=True, blank=True)

    difficulty = models.CharField(max_length=1,
                                  choices=(
                                      ('B', _('Beginner')),
                                      ('I', _('Intermediate')),
                                      ('E', _('Experienced')),
                                  ))

    duration = models.CharField(max_length=1,
                                choices=(
                                    ('S', _('25 mins')),
                                    ('L', _('40 mins')),
                                ))

    language = models.CharField(max_length=1,
                                choices=(
                                    ('E', _('English')),
                                    ('K', _('Korean')),
                                ),
                                default='E')

    def __str__(self):
        return self.title


class TutorialProposal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    brief = models.TextField(max_length=1000)
    desc = models.TextField()
    comment = models.TextField(max_length=4000, null=True, blank=True)

    difficulty = models.CharField(max_length=1,
                                  choices=(
                                      ('B', _('Beginner')),
                                      ('I', _('Intermediate')),
                                      ('E', _('Experienced')),
                                  ))

    duration = models.CharField(max_length=1,
                                choices=(
                                    ('S', _('1 hour')),
                                    ('M', _('2 hours')),
                                    ('L', _('4 hours')),
                                ))

    language = models.CharField(max_length=1,
                                choices=(
                                    ('E', _('English')),
                                    ('K', _('Korean')),
                                ),
                                default='E')

    capacity = models.CharField(max_length=1,
                                choices=(
                                    ('S', _('10 people')),
                                    ('M', _('45 people')),
                                    ('L', _('100 people')),
                                ))
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tutorial', args=[self.id])


class SprintProposal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    language = models.CharField(max_length=255)
    project_url = models.CharField(max_length=1024)
    project_brief = models.TextField(max_length=1000)
    contribution_desc = models.TextField()
    comment = models.TextField(max_length=4000, null=True, blank=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('sprint', args=[self.id])


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, null=True, blank=True)
    organization = models.CharField(max_length=100, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    image = SorlImageField(upload_to='profile', null=True, blank=True)
    bio = models.TextField(max_length=4000, null=True, blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    def get_absolute_url(self):
        return reverse('profile')

    @property
    def is_empty(self):
        return self.name == '' or self.phone is None or self.organization is None or self.bio is None


class Product(object):  # product is not django model now.
    @property
    def price(self):
        return 15000

    @property
    def name(self):
        return 'PyCon Korea 2017'


class Banner(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=255, null=True, blank=True)
    image = SorlImageField(upload_to='banner')
    desc = models.TextField(null=True, blank=True)

    begin = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)


class Preference(models.Model):
    user = models.ForeignKey(User)
    program = models.ForeignKey(Program)

    class Meta:
        unique_together = ('user', 'program')


class TutorialCheckin(models.Model):
    user = models.ForeignKey(User)
    tutorial = models.ForeignKey(TutorialProposal)

    class Meta:
        unique_together = ('user', 'tutorial')


class SprintCheckin(models.Model):
    user = models.ForeignKey(User)
    sprint = models.ForeignKey(SprintProposal)

    class Meta:
        unique_together = ('user', 'sprint')
