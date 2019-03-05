from random import shuffle

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from apps.game.models import Challenge, Game, Competition, TeamParticipatesChallenge, TeamSubmission, Trial, Question, \
    MultipleChoiceQuestion, FileUploadQuestion, PhaseInstructionSet, Instruction, MultipleAnswerQuestion, \
    IntervalQuestion, Choice, Answer, QuestionSubmission, TrialSubmission, CodeUploadQuestion, ReportUploadQuestion, \
    Notification

from apps.game.models.challenge import UserAcceptsTeamInChallenge


class ChallengeInline(admin.StackedInline):
    model = Challenge
    extra = 1
    show_change_link = True


class CompetitionInline(admin.StackedInline):
    model = Competition
    extra = 1
    show_change_link = True


class TeamParticipatesChallengeInline(admin.StackedInline):
    model = TeamParticipatesChallenge
    extra = 1
    show_change_link = True


class GameAdmin(admin.ModelAdmin):
    fields = ['name', 'infra_token']

    inlines = [ChallengeInline]

    list_display = ('id', 'name')
    # list_filter = []

    # search_fields = []


class NotifAdmin(admin.ModelAdmin):
    fields = ['team', 'content', 'title']


class TrialAdmin(admin.ModelAdmin):
    fields = ['questions', 'competition', 'start_time', 'end_time', 'team', 'is_final', 'score']


class QuestionSubmissionAdmin(admin.ModelAdmin):
    fields = ['question', 'score', 'trial_submission']


class TrialSubmissionAdmin(admin.ModelAdmin):
    fields = ['score', 'competition', 'trial', 'team']

# class QuestionAdmin(admin.ModelAdmin):
#     fields = ['stmt', 'value', 'correct_answer']


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 1
    show_change_link = True

# class ImageChoiceInline(admin.StackedInline):
#     model = ImageChoice
#     extra = 1
#     show_change_link = True


class MultipleChoiceAdmin(admin.ModelAdmin):
    inlines = [
        ChoiceInline,
        # ImageChoiceInline
    ]

    fields = ['stmt', 'correct_answer', 'type', 'ui_type', 'level', 'group_id', 'doc_id']


class QuestionAdmin(admin.ModelAdmin):
  fields = ['stmt', 'max_score', 'correct_answer', 'type', 'ui_type', 'level', 'group_id', 'doc_id']


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 1
    show_change_link = True
    # fields = ['text', 'question']


class MultipleAnswerAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline
    ]
    fields = ['stmt', 'max_score', 'correct_answer', 'type', 'ui_type', 'level', 'group_id', 'doc_id']


class FileUploadAdmin(admin.ModelAdmin):
  fields = ['stmt', 'max_score', 'correct_answer', 'type', 'ui_type', 'level', 'dataset_path', 'upload_url', 'group_id', 'doc_id']


class CodeUploadAdmin(admin.ModelAdmin):
    fields = ['stmt', 'max_score', 'correct_answer', 'type', 'ui_type', 'level', 'group_id', 'doc_id']


class ReportUploadAdmin(admin.ModelAdmin):
    fields = ['stmt', 'max_score', 'correct_answer', 'type', 'ui_type', 'level', 'group_id', 'doc_id']


class IntervalQuestionAdmin(admin.ModelAdmin):
    fields = ['stmt', 'max_score', 'correct_answer', 'type', 'ui_type', 'level', 'min_range', 'max_range', 'group_id', 'doc_id']



class PhaseInstructionSetAdmin(admin.ModelAdmin):
    fields = ['phase']


class InstructionAdmin(admin.ModelAdmin):
    fields = ['model_name', 'type', 'app', 'number', 'level', 'phase_instruction_set']



class ChallengeAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Challenge', {'fields': ['title', 'description', 'registration_open', 'scoreboard_freeze_time']}),
        ('Challenge Information', {'fields': ['game', 'team_size', 'entrance_price']}),
        ('Challenge Timing', {'fields': ['registration_start_time', 'registration_end_time',
                                         'start_time', 'end_time', 'is_submission_open']})
    ]
    inlines = [CompetitionInline, TeamParticipatesChallengeInline]

    list_display = ('id', 'title')
    list_filter = ['game', 'registration_open']

    # search_fields = []


class CompetitionAdmin(admin.ModelAdmin):
    fields = ['challenge', 'name', 'tag', 'trial_duration', 'start_time', 'end_time', 'scoreboard_freeze_time', 'trial_per_day', 'type', 'trial_submit_type']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter


class StatusListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('status')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'status'

    def lookups(self, request, MatchAdmin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('running', _('running')),
            ('failed', _('failed')),
            ('done', _('done')),
            ('waiting', _('waiting')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value
        # to decide how to filter the queryset.
        if self.value() == 'running':
            match_pks = [obj.pk for obj in queryset if obj.status == 'running']
            return queryset.filter(pk__in=match_pks)
        if self.value() == 'failed':
            match_pks = [obj.pk for obj in queryset if obj.status == 'failed']
            return queryset.filter(pk__in=match_pks)
        if self.value() == 'done':
            match_pks = [obj.pk for obj in queryset if obj.status == 'done']
            return queryset.filter(pk__in=match_pks)
        if self.value() == 'waiting':
            match_pks = [obj.pk for obj in queryset if obj.status == 'waiting']
            return queryset.filter(pk__in=match_pks)


class IsReadyToRunListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('is ready')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'is ready'

    def lookups(self, request, MatchAdmin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('True', _('True')),
            ('False', _('False')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value
        # to decide how to filter the queryset.
        if self.value() == 'True':
            match_pks = [obj.pk for obj in queryset if obj.is_ready_to_run() == True]
            return queryset.filter(pk__in=match_pks)
        if self.value() == 'False':
            match_pks = [obj.pk for obj in queryset if obj.is_ready_to_run() == False]
            return queryset.filter(pk__in=match_pks)



# class TeamSubmissionAdmin(admin.ModelAdmin):
#     fields = ['team', 'file', 'language', 'is_final', 'time', 'infra_compile_message']
#
#     inlines = [Inline]
#
#     list_display = ('id', 'title')
#     list_filter = ['game', 'registraion_open']
#
#     # search_fields = []


admin.site.register(Game, GameAdmin)

admin.site.register(Challenge, ChallengeAdmin)
# admin.site.register(TeamSubmission, TeamSubmissionAdmin)

admin.site.register(Competition, CompetitionAdmin)

admin.site.register(UserAcceptsTeamInChallenge)
# admin.site.register(Participant)


class MapAdmin(admin.ModelAdmin):
    fields = ['name', 'file', 'token', 'competitions']
    readonly_fields = ['token']


admin.site.register(TeamSubmission)
admin.site.register(Trial, TrialAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceAdmin)
admin.site.register(FileUploadQuestion, FileUploadAdmin)
admin.site.register(MultipleAnswerQuestion,  MultipleAnswerAdmin)
admin.site.register(IntervalQuestion, IntervalQuestionAdmin)
admin.site.register(PhaseInstructionSet, PhaseInstructionSetAdmin)
admin.site.register(Instruction, InstructionAdmin)
admin.site.register(QuestionSubmission, QuestionSubmissionAdmin)
admin.site.register(TrialSubmission, TrialSubmissionAdmin)
admin.site.register(CodeUploadQuestion, CodeUploadAdmin)
admin.site.register(ReportUploadQuestion, ReportUploadAdmin)
admin.site.register(Notification, NotifAdmin)