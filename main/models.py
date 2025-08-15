from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import secrets
from datetime import timedelta

# -------------------------------
# User Profile
# -------------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message}"


from django.db import models

class LearningEnvironmentImage(models.Model):
    title = models.CharField(max_length=100, blank=True)  # Optional caption
    image = models.ImageField(upload_to='learning_environment/')  # Saved in MEDIA folder
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Image {self.pk}"



# -------------------------------
# Current Affairs
# -------------------------------
class CurrentAffairPDF(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    pdf = models.FileField(upload_to='current_affairs_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# -------------------------------
# General Mock Tests
# -------------------------------
class MockTest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title

    def question_count(self):
        return self.questions.count()


class MockQuestion(models.Model):
    mock_test = models.ForeignKey(MockTest, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )

    def __str__(self):
        return self.question_text[:50]


class MockTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mock_test = models.ForeignKey(MockTest, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.mock_test.title} ({self.score}/{self.total_questions})"



# -------------------------------
# PSC Section
# -------------------------------
class PscCourse(models.Model):
    name = models.CharField(max_length=200)
    details = models.TextField()

    def __str__(self):
        return self.name


class PscVideoClass(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_link = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PscMockTest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PscMockQuestion(models.Model):
    psc_mock_test = models.ForeignKey(PscMockTest, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')]
    )

    def __str__(self):
        return self.question_text[:50]


class PscPreviousYearQuestion(models.Model):
    exam_name = models.CharField(max_length=200)
    year = models.CharField(max_length=20)
    pdf_file = models.FileField(upload_to='pyqs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam_name} ({self.year})"


# -------------------------------
# Daily Quiz
# -------------------------------
class DailyQuiz(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(unique=True)  # Only one quiz per date
    duration_minutes = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.title} ({self.date})"


class DailyQuestion(models.Model):
    quiz = models.ForeignKey(DailyQuiz, on_delete=models.CASCADE, related_name="questions")

    # Malayalam
    question_text_ml = models.TextField()
    option_a_ml = models.CharField(max_length=200)
    option_b_ml = models.CharField(max_length=200)
    option_c_ml = models.CharField(max_length=200)
    option_d_ml = models.CharField(max_length=200)

    # English
    question_text_en = models.TextField(blank=True, null=True)
    option_a_en = models.CharField(max_length=200, blank=True, null=True)
    option_b_en = models.CharField(max_length=200, blank=True, null=True)
    option_c_en = models.CharField(max_length=200, blank=True, null=True)
    option_d_en = models.CharField(max_length=200, blank=True, null=True)

    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        default='A'
    )

    def __str__(self):
        return f"{self.quiz.title}: {self.question_text_ml[:40]}"


class DailyQuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(DailyQuiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField(default=0)
    skipped = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.date} - {self.score}/{self.total_questions}"


# ========================
# SSC VIDEO CLASSES
# ========================
class SscVideoClass(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    video_link = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ========================
# SSC MOCK TESTS
# ========================
class SscMockTest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SscMockQuestion(models.Model):
    mock_test = models.ForeignKey(SscMockTest, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )

    def __str__(self):
        return f"{self.mock_test.title} - {self.question_text[:50]}"


class SscMockTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mock_test = models.ForeignKey(SscMockTest, on_delete=models.CASCADE)
    score = models.IntegerField()
    completed = models.BooleanField(default=False)
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.mock_test.title} ({self.score})"


# ========================
# SSC PREVIOUS YEAR QUESTIONS
# ========================
class SscPreviousYearQuestion(models.Model):
    exam_name = models.CharField(max_length=200)
    year = models.CharField(max_length=10)
    pdf_file = models.FileField(upload_to="ssc_pyq/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam_name} - {self.year}"


# ========================
# SSC CURRENT AFFAIRS
# ========================
class SscCurrentAffairPDF(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    pdf = models.FileField(upload_to="ssc_current_affairs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# RRB Video Classes
# =========================
class RrbVideoClass(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    video_link = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# RRB Mock Test + Questions
# =========================
class RrbMockTest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class RrbMockQuestion(models.Model):
    mock_test = models.ForeignKey(RrbMockTest, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(
        max_length=1,
        choices=[("A", "Option A"), ("B", "Option B"), ("C", "Option C"), ("D", "Option D")]
    )

    def __str__(self):
        return f"{self.mock_test.title} - {self.question_text[:50]}"


class RrbMockTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mock_test = models.ForeignKey(RrbMockTest, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.mock_test.title} ({self.score})"


# =========================
# RRB Previous Year Questions
# =========================
class RrbPreviousYearQuestion(models.Model):
    exam_name = models.CharField(max_length=200)
    year = models.CharField(max_length=10)  # increased length for safety
    pdf_file = models.FileField(upload_to="rrb_pyqs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam_name} - {self.year}"


# =========================
# RRB Current Affairs PDFs
# =========================
class RrbCurrentAffairPDF(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    pdf = models.FileField(upload_to="rrb_current_affairs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# -------------------------------
# Subscription
# -------------------------------
class Subscription(models.Model):
    PLAN_CHOICES = [
        ('FREE', 'Free Plan'),
        ('PREMIUM', 'Premium Plan'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='FREE')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        return bool(self.end_date and self.end_date >= timezone.now())

    def __str__(self):
        return f"{self.user.username} - {self.plan}"





class PasswordResetOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hashed_otp = models.CharField(max_length=255)
    channel = models.CharField(max_length=10, default='email')  # Always email
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def _generate_code(length=6):
        # secure numeric code, zero-padded
        return str(secrets.randbelow(10**length)).zfill(length)

    @classmethod
    def create_for_user(cls, user, ttl_minutes=10):
        code = cls._generate_code()
        hashed = make_password(code)
        expires = timezone.now() + timedelta(minutes=ttl_minutes)
        otp = cls.objects.create(user=user, hashed_otp=hashed, expires_at=expires)
        return otp, code

    def __str__(self):
        return f"OTP for {self.user} via email (used={self.is_used})"
