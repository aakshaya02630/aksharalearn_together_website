from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import login_view


urlpatterns = [
    path("", views.home, name="home"),
    path("subscription/", views.subscription, name="subscription"),
    path('payment-success/', views.payment_success, name='payment_success'),
    path("notifications/", views.notifications_view, name="notifications"),
    path("register/", views.register_views, name="register"),


    # Search
    path("search/", views.search, name="search"),

    # Mock Tests
    path("mocktest/", views.mocktest_list, name="mocktest_list"),
    path("mocktest/<int:test_id>/", views.mocktest_detail, name="mocktest_detail"),
    path("mocktest/<int:test_id>/result/", views.mocktest_result, name="mocktest_result"),

    # PSC
    path("psc/", views.psc, name="psc"),
    path("psc_mocktest/<int:test_id>/", views.psc_mocktest, name="psc_mocktest"),

    # SSC
    path("ssc/", views.ssc, name="ssc"),
    path("ssc/mocktest/<int:test_id>/", views.ssc_mocktest, name="ssc_mocktest"),

    # RRB
    path("rrb/", views.rrb, name="rrb"),
    path("rrb/mocktest/<int:test_id>/", views.rrb_mocktest, name="rrb_mocktest"),

    # Daily Quiz
    path("quiz/", views.daily_quiz_view, name="daily_quiz"),
    path("quiz/<int:quiz_id>/result/", views.quiz_result_view, name="quiz_result"),
    path("quiz/progress/", views.quiz_progress_view, name="quiz_progress"),

    path('password-reset/request/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/verify/', views.password_reset_verify, name='password_reset_verify'),

    path('profile/', views.profile, name='profile'),
    #login
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

]

