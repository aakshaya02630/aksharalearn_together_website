from django.contrib import admin
from import_export import resources,fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from datetime import date

from .models import (
    UserProfile,
    CurrentAffairPDF,
    PscVideoClass,
    MockTest,
    MockQuestion,
    MockTestResult,
    PscPreviousYearQuestion,
    DailyQuiz,
    DailyQuestion,
    DailyQuizSubmission,
    PscMockTest,
    PscMockQuestion,
    SscVideoClass,
    SscMockTest,
    SscMockQuestion,
    SscMockTestResult,
    SscPreviousYearQuestion,
    SscCurrentAffairPDF,
    Subscription,
    LearningEnvironmentImage,

)

# ----------------------------
# USER PROFILE ADMIN
# ----------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')


#learninimage
@admin.register(LearningEnvironmentImage)
class LearningEnvironmentImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')


# ----------------------------
# CURRENT AFFAIRS ADMIN
# ----------------------------
@admin.register(CurrentAffairPDF)
class CurrentAffairPDFAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    search_fields = ('title',)
    ordering = ('-uploaded_at',)


# ----------------------------
# PSC VIDEO CLASSES ADMIN
# ----------------------------
@admin.register(PscVideoClass)
class PscVideoClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_link', 'uploaded_at')
    search_fields = ('title',)
    ordering = ('-uploaded_at',)


# ----------------------------
# PSC MOCK TESTS ADMIN
# ----------------------------
class PscMockQuestionInline(admin.TabularInline):
    model = PscMockQuestion
    extra = 20  # allow up to 20 questions inline

@admin.register(PscMockTest)
class PscMockTestAdmin(admin.ModelAdmin):
    inlines = [PscMockQuestionInline]
    list_display = ('title', 'description', 'created_at')
    search_fields = ('title',)

# ----------------------------
# PSC PREVIOUS YEAR QUESTIONS ADMIN
# ----------------------------
@admin.register(PscPreviousYearQuestion)
class PscPreviousYearQuestionAdmin(admin.ModelAdmin):
    list_display = ('exam_name', 'year', 'pdf_file', 'uploaded_at')
    search_fields = ('exam_name', 'year')
    ordering = ('-uploaded_at',)

# ----------------------------
# DAILY QUIZ ADMIN
# ----------------------------
@admin.register(DailyQuiz)
class DailyQuizAdmin(ImportExportModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title',)


# ----------------------------
# DAILY QUESTION ADMIN (with import/export)
# ----------------------------

class DailyQuestionResource(resources.ModelResource):
    quiz = fields.Field(
        column_name='quiz__title',   # Column in your CSV
        attribute='quiz',
        widget=ForeignKeyWidget(DailyQuiz, 'title')
    )

    class Meta:
        model = DailyQuestion
        fields = (
            'quiz',
            'question_text_ml',
            'option_a_ml',
            'option_b_ml',
            'option_c_ml',
            'option_d_ml',
            'question_text_en',
            'option_a_en',
            'option_b_en',
            'option_c_en',
            'option_d_en',
            'correct_option',
        )
        exclude = ('id',)
        import_id_fields = ['question_text_ml']  # Unique per question

    def before_import_row(self, row, **kwargs):
        """Create quiz automatically if not found"""
        quiz_title = row.get('quiz__title')
        if quiz_title:
            DailyQuiz.objects.get_or_create(
                title=quiz_title,
                defaults={'date': date.today(), 'duration_minutes': 10}
            )

@admin.register(DailyQuestion)
class DailyQuestionAdmin(ImportExportModelAdmin):
    resource_class = DailyQuestionResource
    list_display = ('quiz_title', 'question_text_ml', 'correct_option')
    search_fields = ('question_text_ml', 'quiz__title')
    list_filter = ('quiz',)

    def quiz_title(self, obj):
        return obj.quiz.title if obj.quiz else "-"
    quiz_title.short_description = "Quiz"


@admin.register(DailyQuizSubmission)
class DailyQuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'total_questions', 'skipped', 'submitted_at')
    search_fields = ('user__username', 'quiz__title')
    list_filter = ('quiz', 'submitted_at')



 # Inline for adding questions inside MockTest
class SscMockQuestionInline(admin.TabularInline):
    model = SscMockQuestion
    extra = 20  # By default show 20 blank fields for questions

@admin.register(SscMockTest)
class SscMockTestAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "created_at")
    search_fields = ("title",)
    inlines = [SscMockQuestionInline]

@admin.register(SscVideoClass)
class SscVideoClassAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_at")
    search_fields = ("title",)

@admin.register(SscPreviousYearQuestion)
class SscPreviousYearQuestionAdmin(admin.ModelAdmin):
    list_display = ("exam_name", "year", "uploaded_at")
    search_fields = ("exam_name", "year")

@admin.register(SscCurrentAffairPDF)
class SscCurrentAffairPDFAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_at")
    search_fields = ("title",)

@admin.register(SscMockTestResult)
class SscMockTestResultAdmin(admin.ModelAdmin):
    list_display = ("user", "mock_test", "score", "completed", "taken_at")
    search_fields = ("user__username", "mock_test__title")

from django.contrib import admin
from .models import (
    RrbVideoClass,
    RrbMockTest,
    RrbMockQuestion,
    RrbMockTestResult,
    RrbPreviousYearQuestion,
    RrbCurrentAffairPDF,
)


# Inline for adding questions inside MockTest
class RrbMockQuestionInline(admin.TabularInline):
    model = RrbMockQuestion
    extra = 20  # Show 20 blank question fields by default


@admin.register(RrbMockTest)
class RrbMockTestAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "created_at")
    search_fields = ("title",)
    inlines = [RrbMockQuestionInline]


@admin.register(RrbVideoClass)
class RrbVideoClassAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_at")
    search_fields = ("title",)


@admin.register(RrbPreviousYearQuestion)
class RrbPreviousYearQuestionAdmin(admin.ModelAdmin):
    list_display = ("exam_name", "year", "uploaded_at")
    search_fields = ("exam_name", "year")


@admin.register(RrbCurrentAffairPDF)
class RrbCurrentAffairPDFAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_at")
    search_fields = ("title",)


@admin.register(RrbMockTestResult)
class RrbMockTestResultAdmin(admin.ModelAdmin):
    list_display = ("user", "mock_test", "score", "completed", "taken_at")
    search_fields = ("user__username", "mock_test__title")



@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date')
    search_fields = ('user__username', 'plan')
