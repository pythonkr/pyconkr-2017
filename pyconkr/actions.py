from .models import (Program, Speaker)


def convert_proposal_to_program(modeladmin, request, queryset):
    # prepare speaker
    for proposal in queryset:
        speaker, _ = Speaker.objects.get_or_create(email=proposal.user.email)
        program, _ = Program.objects.get_or_create(name=proposal.title)

        # Set initial data
        speaker.slug = proposal.user.email
        speaker.name = proposal.user.profile.name
        speaker.desc = proposal.user.profile.bio
        speaker.organization = proposal.user.profile.organization
        speaker.save()

        program.brief = proposal.brief
        program.desc = proposal.desc
        program.difficulty = proposal.difficulty
        program.duration = proposal.duration
        program.language = proposal.language
        program.speakers.clear()
        program.speakers.add(speaker)
        program.save()

        print(program, speaker)
