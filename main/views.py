# Django core
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import login




# Django forms & email
from django.core.mail import send_mail
from .forms import RequestOTPForm, VerifyOTPForm

# Python standard library
from datetime import timedelta

import random


# Razorpay
import razorpay

# Your app models
from .models import (
    UserProfile,
    Subscription,
    CurrentAffairPDF,
    MockTest,
    MockQuestion,
    MockTestResult,
    PscPreviousYearQuestion,
    PscVideoClass,
    DailyQuiz,
    DailyQuestion,
    DailyQuizSubmission,

    RrbVideoClass,
    RrbMockTest,
    RrbMockQuestion,
    RrbMockTestResult,
    RrbPreviousYearQuestion,
    RrbCurrentAffairPDF,
    Notification,

    SscVideoClass,
    SscMockTest,
    SscMockQuestion,
    SscMockTestResult,
    SscPreviousYearQuestion,
    SscCurrentAffairPDF,

    PasswordResetOTP,
    LearningEnvironmentImage# Required for email OTP
)


# ========================
# AUTHENTICATION VIEWS
# ========================

def home(request):
    learning_images = LearningEnvironmentImage.objects.all()
    return render(request, 'home.html', {
        'learning_images': learning_images
    })




def register_views(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        confirm = request.POST['confirm_password']

        if password != confirm:
            return render(request, 'register.html', {'error': "Passwords do not match"})

        if User.objects.filter(username=email).exists():
            return render(request, 'register.html', {'error': "Email already registered"})

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            UserProfile.objects.create(user=user, phone=phone)
            login(request, user)  # Auto login

            # Add success message
            messages.success(request, "Registered successfully! Welcome, " + name)
            return redirect('home')  # You can redirect wherever you want
        except Exception as e:
            print("❌ Error:", e)

        return render(request, 'register.html', {'error': "Something went wrong. Try again."})
    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('home')  # Change 'home' to your homepage route
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')

    return render(request, 'login.html')

# ========================
# MOCK TEST VIEWS
# ========================
@login_required
def mocktest_list(request):
    subscription = Subscription.objects.filter(user=request.user).first()
    tests = MockTest.objects.all().order_by('id')  # ensure consistent order

    # Track progress
    progress = {}
    for test in tests:
        result = MockTestResult.objects.filter(user=request.user, mock_test=test).first()
        progress[test.id] = {
            "completed": result.completed if result else False,
            "score": result.score if result else None,
        }

    progress_objects = []
    for test in tests:
        progress_objects.append({
            "test": test,
            "completed": progress[test.id]["completed"],
            "score": progress[test.id]["score"],
        })

    # Identify the trial test (first one)
    trial_test = tests.first()

    # Check access:
    # - Always allow the trial test
    # - Allow all tests only if subscription is PREMIUM
    return render(request, 'mocktest_list.html', {
        "progress_objects": progress_objects,
        "trial_test": trial_test,
        "has_premium": subscription and subscription.plan == "PREMIUM"
    })


@login_required
def mocktest_detail(request, test_id):
    test = get_object_or_404(MockTest, id=test_id)
    questions = test.questions.all()

    if request.method == "POST":
        score = 0
        total = questions.count()

        for q in questions:
            selected = request.POST.get(str(q.id))
            if selected == q.correct_option:
                score += 1

        # Save the result
        MockTestResult.objects.update_or_create(
            user=request.user,
            mock_test=test,
            defaults={"score": score, "completed": True},
        )

        return redirect("mocktest_result", test_id=test.id)

    return render(request, "mocktest_detail.html", {
        "test": test,
        "questions": questions
    })



@login_required
def psc_mocktest(request, test_id):
    """View for a single PSC mock test"""
    mock_test = get_object_or_404(MockTest, id=test_id)
    questions = mock_test.questions.all()

    if request.method == 'POST':
        score = 0
        total = questions.count()

        for question in questions:
            selected = request.POST.get(f'question_{question.id}')
            if selected == question.correct_option:
                score += 1

        return render(request, 'psc_mocktest_result.html', {
            'mock_test': mock_test,
            'score': score,
            'total': total
        })

    return render(request, 'psc_mocktest.html', {
        'mock_test': mock_test,
        'questions': questions
    })


@login_required
def mocktest_result(request, test_id):
    mock_test = get_object_or_404(MockTest, id=test_id)
    result = get_object_or_404(MockTestResult, user=request.user, mock_test=mock_test)

    total_questions = mock_test.questions.count()
    correct_answers = result.score
    wrong_answers = total_questions - correct_answers

    return render(request, "mocktest_result.html", {
        "mock_test": mock_test,
        "result": result,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
    })
# ========================
# PSC PAGE
# ========================

@login_required(login_url='login')
def psc(request):
    section = request.GET.get("section", "video")
    subscription = Subscription.objects.filter(user=request.user).first()

    if not subscription or subscription.plan != "PREMIUM":
        return render(request, 'psc.html', {
            "needs_subscription": True,
            "section": section,
            "current_affairs": [],
            "mock_tests": [],
            "pyqs": [],
            "video_classes": []
        })

    current_affairs = CurrentAffairPDF.objects.order_by('-uploaded_at')
    mock_tests = MockTest.objects.all().order_by('-id')
    pyqs = PscPreviousYearQuestion.objects.all().order_by('-uploaded_at')
    video_classes = PscVideoClass.objects.all().order_by('-uploaded_at')

    return render(request, 'psc.html', {
        "section": section,
        "needs_subscription": False,
        "current_affairs": current_affairs,
        "mock_tests": mock_tests,
        "pyqs": pyqs,
        "video_classes": video_classes
    })


# ========================
# SEARCH FUNCTION
# ========================

@login_required
def search(request):
    query = request.GET.get('query', '')
    mocktests = pyqs = []

    if query:
        mocktests = MockTest.objects.filter(title__icontains=query)
        pyqs = PscPreviousYearQuestion.objects.filter(exam_name__icontains=query)

    return render(request, 'home.html', {
        'query': query,
        'mocktests': mocktests,
        'pyqs': pyqs,
    })


# ========================
# DAILY QUIZ
# ========================

@login_required
def daily_quiz_view(request):
    quiz = DailyQuiz.objects.filter(date=timezone.now().date()).first()

    if not quiz:
        return render(request, "daily_quiz.html", {"no_quiz": True})

    submission = DailyQuizSubmission.objects.filter(user=request.user, quiz=quiz).first()

    if request.method == "POST":
        if not submission:
            score = 0
            skipped = 0
            total = quiz.questions.count()

            for q in quiz.questions.all():
                answer = request.POST.get(str(q.id))
                if not answer:
                    skipped += 1
                elif answer == q.correct_option:
                    score += 1

            submission = DailyQuizSubmission.objects.create(
                user=request.user, quiz=quiz, score=score,
                total_questions=total, skipped=skipped
            )

        # ✅ Always redirect to result page
        return redirect("quiz_result", quiz_id=quiz.id)

    # if GET
    translated_questions = []
    for q in quiz.questions.all():
        translated_questions.append({
            "id": q.id,
            "ml": {"question": q.question_text_ml, "A": q.option_a_ml, "B": q.option_b_ml, "C": q.option_c_ml, "D": q.option_d_ml},
            "en": {"question": q.question_text_en, "A": q.option_a_en, "B": q.option_b_en, "C": q.option_c_en, "D": q.option_d_en},
        })

    return render(request, "daily_quiz.html", {
        "quiz": quiz,
        "questions": translated_questions,
        "submission": submission
    })


@login_required
def quiz_result_view(request, quiz_id):
    submission = DailyQuizSubmission.objects.filter(user=request.user, quiz_id=quiz_id).first()
    quiz = DailyQuiz.objects.get(id=quiz_id)
    return render(request, "quiz_result.html", {"submission": submission, "quiz": quiz})


@login_required
def quiz_progress_view(request):
    submissions = DailyQuizSubmission.objects.filter(user=request.user).order_by("quiz__date")
    return render(request, "quiz_progress.html", {"submissions": submissions})


# ========================
# SSC PAGE
# ========================

@login_required(login_url='login')
def ssc(request):
    section = request.GET.get("section", None)
    subscription = Subscription.objects.filter(user=request.user).first()

    if not subscription or subscription.plan != "PREMIUM":
        return render(request, "ssc.html", {
            "needs_subscription": True,
            "section": section,
            "video_classes": [],
            "mock_tests": [],
            "pyqs": [],
            "current_affairs": [],
        })

    video_classes = SscVideoClass.objects.all().order_by("-uploaded_at")
    mock_tests = SscMockTest.objects.all().order_by("-id")
    pyqs = SscPreviousYearQuestion.objects.all().order_by("-uploaded_at")
    current_affairs = SscCurrentAffairPDF.objects.all().order_by("-uploaded_at")

    return render(request, "ssc.html", {
        "needs_subscription": False,
        "section": section,
        "video_classes": video_classes,
        "mock_tests": mock_tests,
        "pyqs": pyqs,
        "current_affairs": current_affairs,
    })


@login_required
def ssc_mocktest(request, test_id):
    test = get_object_or_404(SscMockTest, id=test_id)
    questions = test.questions.all()

    if request.method == "POST":
        score = 0
        total = questions.count()

        for q in questions:
            selected = request.POST.get(str(q.id))
            if selected == q.correct_option:
                score += 1

        percentage = (score / total) * 100 if total > 0 else 0

        SscMockTestResult.objects.update_or_create(
            user=request.user,
            mock_test=test,
            defaults={"score": score, "completed": True},
        )

        return render(request, "ssc_mocktest_result.html", {
            "test": test,
            "score": score,
            "total": total,
            "percentage": round(percentage, 2)
        })

    return render(request, "ssc_mocktest.html", {
        "test": test,
        "questions": questions
    })


# ========================
# RRB PAGE
# ========================
@login_required(login_url='login')
def rrb(request):
    section = request.GET.get("section", None)
    subscription = Subscription.objects.filter(user=request.user).first()

    # Check if user has a valid subscription
    if not subscription or subscription.plan != "PREMIUM":
        return render(request, "rrb.html", {
            "needs_subscription": True,
            "section": section,
            "video_classes": [],
            "mock_tests": [],
            "pyqs": [],
            "current_affairs": [],
        })

    # If subscribed, fetch data
    video_classes = RrbVideoClass.objects.all().order_by("-uploaded_at")
    mock_tests = RrbMockTest.objects.all().order_by("-id")
    pyqs = RrbPreviousYearQuestion.objects.all().order_by("-uploaded_at")
    current_affairs = RrbCurrentAffairPDF.objects.all().order_by("-uploaded_at")

    return render(request, "rrb.html", {
        "needs_subscription": False,
        "section": section,
        "video_classes": video_classes,
        "mock_tests": mock_tests,
        "pyqs": pyqs,
        "current_affairs": current_affairs,
    })
@login_required
def rrb_mocktest(request, test_id):
    mock_test = get_object_or_404(RrbMockTest, id=test_id)
    questions = mock_test.questions.all()

    if request.method == 'POST':
        score = 0
        total = questions.count()

        for question in questions:
            selected = request.POST.get(f'question_{question.id}')
            if selected == question.correct_option:
                score += 1

        RrbMockTestResult.objects.update_or_create(
            user=request.user,
            mock_test=mock_test,
            defaults={"score": score, "completed": True},
        )

        return render(request, 'rrb_mocktest_result.html', {
            'mock_test': mock_test,
            'score': score,
            'total': total,
        })

    return render(request, 'rrb_mocktest.html', {
        'mock_test': mock_test,
        'questions': questions,
    })


# ========================
# SUBSCRIPTION PAGE
# ========================


@login_required
def subscription(request):
    if request.method == "POST":
        # Step 1: Create Razorpay Order for ₹99
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        DATA = {
            "amount": 9900,  # ₹99 in paise
            "currency": "INR",
            "payment_capture": 1,
        }
        order = client.order.create(data=DATA)

        # Step 2: Render payment page with Razorpay order details
        return render(request, "subscription.html", {
            "order_id": order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": DATA["amount"],
            "currency": DATA["currency"],
        })

    return render(request, "subscription.html")


@login_required
def payment_success(request):
    # Save subscription after successful payment
    duration = 30
    end_date = timezone.now() + timedelta(days=duration)

    Subscription.objects.update_or_create(
        user=request.user,
        defaults={
            "plan": "PREMIUM",
            "start_date": timezone.now(),
            "end_date": end_date,
        }
    )

    # Send email
    subject = "🎉 Subscription Successful - Akshara Learn Together"
    message = f"""
    Hi {request.user.username},

    Thank you for your payment! 🎉
    Your Premium Plan is now active.

    Plan: PREMIUM
    Start Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}
    End Date: {end_date.strftime('%Y-%m-%d %H:%M')}

    Happy Learning!
    - Akshara Learn Together Team
    """
    recipient = request.user.email
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])

    messages.success(request, "🎉 Payment successful! Subscribed to PREMIUM plan.")
    return redirect("home")


# ========================
# NOTIFICATIONS
# ========================

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})




# Helper: send OTP by email
def send_otp_email(user, code):
    subject = "Your password reset OTP"
    message = f"Your OTP is {code}. It expires in 10 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def password_reset_request(request):
    if request.method == "POST":
        form = RequestOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip()
            User = get_user_model()
            user = User.objects.filter(email__iexact=email).first()

            if user:
                otp_obj, code = PasswordResetOTP.create_for_user(user, ttl_minutes=10)
                try:
                    send_otp_email(user, code)
                except Exception:
                    messages.error(request, "Failed to send OTP. Please try again.")
                    return redirect('password_reset_request')

                request.session['password_reset_otp_id'] = otp_obj.id
                messages.success(request, "An OTP has been sent to your email.")
                return redirect('password_reset_verify')
            else:
                # Security: do NOT reveal if the email exists
                messages.success(request, "If an account exists with this email, an OTP has been sent.")

                # Set session flag to allow OTP page
                request.session['password_reset_allowed'] = True
                return redirect('password_reset_verify')
    else:
        form = RequestOTPForm()

    return render(request, 'password_reset_request.html', {'form': form})


def password_reset_verify(request):
    otp_id = request.session.get('password_reset_otp_id')
    allowed = request.session.get('password_reset_allowed', False)

    if not otp_id and not allowed:
        messages.error(request, "Please request an OTP first.")
        return redirect('password_reset_request')

    otp_obj = None
    if otp_id:
        otp_obj = PasswordResetOTP.objects.filter(id=otp_id, is_used=False).first()

    if otp_obj and otp_obj.is_expired():
        messages.error(request, "OTP expired or invalid. Please request again.")
        return redirect('password_reset_request')

    if request.method == "POST":
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp'].strip()
            new_password1 = form.cleaned_data['new_password1']
            new_password2 = form.cleaned_data['new_password2']

            if new_password1 != new_password2:
                messages.error(request, "Passwords do not match.")
            else:
                # Check OTP
                if otp_obj and check_password(entered_otp, otp_obj.hashed_otp):
                    user = otp_obj.user
                    user.set_password(new_password1)
                    user.save()

                    otp_obj.is_used = True
                    otp_obj.save()

                    request.session.pop('password_reset_otp_id', None)
                    messages.success(request, "Password updated successfully. Please login.")
                    return redirect('login')
                else:
                    if otp_obj:
                        otp_obj.attempts += 1
                        otp_obj.save()
                        if otp_obj.attempts >= 5:
                            otp_obj.is_used = True
                            otp_obj.save()
                            messages.error(request, "Too many failed attempts. Request a new OTP.")
                            return redirect('password_reset_request')
                    messages.error(request, "Invalid OTP. Try again.")
    else:
        form = VerifyOTPForm()

    return render(request, 'password_reset_verify.html', {'form': form})


#profile
@login_required
def profile(request):
    # Fetch the user's profile from the database
    user_profile = UserProfile.objects.filter(user=request.user).first()
    return render(request, 'profile.html', {'user_profile': user_profile})
