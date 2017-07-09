from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.flatpages.models import FlatPage
from django.db import models
from django_summernote.admin import SummernoteModelAdmin
from django_summernote.widgets import SummernoteWidget
from modeltranslation.admin import TranslationAdmin
from sorl.thumbnail.admin import AdminImageMixin
from .models import (Room, Program, ProgramTime, ProgramDate, ProgramCategory,
                     Speaker, Sponsor, SponsorLevel, Preference,
                     Profile, Announcement, EmailToken, Proposal, Banner,
                     TutorialProposal, TutorialCheckin, SprintProposal)
from .actions import convert_proposal_to_program


class SummernoteWidgetWithCustomToolbar(SummernoteWidget):
    def template_contexts(self):
        contexts = super(SummernoteWidgetWithCustomToolbar, self).template_contexts()
        contexts['width'] = '960px'
        return contexts


class RoomAdmin(SummernoteModelAdmin, TranslationAdmin):
    list_display = ('id', 'name',)
    list_editable = ('name',)
    search_fields = ('name',)
admin.site.register(Room, RoomAdmin)


class ProgramDateAdmin(admin.ModelAdmin):
    list_display = ('id', 'day',)
admin.site.register(ProgramDate, ProgramDateAdmin)


class ProgramTimeAdmin(TranslationAdmin):
    list_display = ('id', 'name', 'begin', 'end', 'day')
    list_editable = ('name', 'day')
    ordering = ('begin',)
admin.site.register(ProgramTime, ProgramTimeAdmin)


class ProgramCategoryAdmin(TranslationAdmin):
    list_display = ('id', 'name', 'slug',)
    list_editable = ('name', 'slug',)
admin.site.register(ProgramCategory, ProgramCategoryAdmin)


class SponsorAdmin(SummernoteModelAdmin, TranslationAdmin):
    formfield_overrides = {models.TextField: {'widget': SummernoteWidgetWithCustomToolbar}}
    list_display = ('id', 'slug', 'name',)
    ordering = ('name',)
    list_editable = ('slug', 'name',)
    search_fields = ('name',)
admin.site.register(Sponsor, SponsorAdmin)


class SponsorLevelAdmin(SummernoteModelAdmin, TranslationAdmin):
    list_display = ('id', 'order', 'name', 'slug',)
    list_editable = ('order', 'name', 'slug',)
    ordering = ('order',)
    search_fields = ('name',)
admin.site.register(SponsorLevel, SponsorLevelAdmin)


class SpeakerAdmin(SummernoteModelAdmin, TranslationAdmin):
    list_display = ('id', 'slug', 'name', 'email',)
    list_editable = ('slug', 'name', 'email',)
    ordering = ('name',)
    search_fields = ('name', 'slug', 'email',)
admin.site.register(Speaker, SpeakerAdmin)


class ProgramAdmin(SummernoteModelAdmin, TranslationAdmin):
    list_display = ('id', 'name', 'date', 'room', 'get_speakers', 'category', 'is_recordable',)
    list_editable = ('name', 'category', 'is_recordable',)
    ordering = ('id',)
    filter_horizontal = ('times', )
    search_fields = ('name', 'speakers__name', 'desc',)
admin.site.register(Program, ProgramAdmin)


class AnnouncementAdmin(SummernoteModelAdmin, TranslationAdmin):
    list_display = ('id', 'title', 'created', 'modified')
    ordering = ('id',)
    search_fields = ('title',)
admin.site.register(Announcement, AnnouncementAdmin)


class EmailTokenAdmin(admin.ModelAdmin):
    list_display = ('email', 'token', 'created')
    search_fields = ('email',)
admin.site.register(EmailToken, EmailTokenAdmin)


class FlatPageAdmin(TranslationAdmin):
    formfield_overrides = {models.TextField: {'widget': SummernoteWidgetWithCustomToolbar}}


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)


class ProfileInline(AdminImageMixin, admin.StackedInline):
    model = Profile
    can_delete = False


class ProposalAdminForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = '__all__'
        widgets = {
            'desc': SummernoteWidgetWithCustomToolbar(),
            'comment': SummernoteWidgetWithCustomToolbar(),
        }


class ProposalAdmin(admin.ModelAdmin):
    form = ProposalAdminForm
    list_display = ('user', 'title', 'difficulty', 'duration', 'language')
    actions = [convert_proposal_to_program]
admin.site.register(Proposal, ProposalAdmin)


class TutorialProposalAdminForm(forms.ModelForm):
    class Meta:
        model = TutorialProposal
        fields = '__all__'
        widgets = {
            'desc': SummernoteWidgetWithCustomToolbar(),
            'comment': SummernoteWidgetWithCustomToolbar(),
        }


class TutorialProposalAdmin(admin.ModelAdmin):
    form = TutorialProposalAdminForm
    list_display = ('user', 'title', 'difficulty', 'duration', 'language', 'capacity')
    actions = [convert_proposal_to_program]
admin.site.register(TutorialProposal, TutorialProposalAdmin)


class SprintProposalAdminForm(forms.ModelForm):
    class Meta:
        model = SprintProposal
        fields = '__all__'
        widgets = {
            'contribution_desc': SummernoteWidgetWithCustomToolbar(),
            'comment': SummernoteWidgetWithCustomToolbar(),
        }


class SprintProposalAdmin(admin.ModelAdmin):
    form = SprintProposalAdminForm
    list_display = ('title', 'language', 'project_url', 'project_brief', 'contribution_desc')
    actions = [convert_proposal_to_program]
admin.site.register(SprintProposal, SprintProposalAdmin)


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class BannerAdmin(SummernoteModelAdmin, TranslationAdmin):
    list_display = ('id', 'name', 'url', 'begin', 'end')
    ordering = ('id',)
    search_fields = ('name', 'url')
admin.site.register(Banner, BannerAdmin)


class PreferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'program',)
admin.site.register(Preference, PreferenceAdmin)


class TutorialCheckinAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tutorial',)
admin.site.register(TutorialCheckin, TutorialCheckinAdmin)
