from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import StyledPasswordResetForm, StyledSetPasswordForm

urlpatterns = [
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("login/", views.UserLoginView.as_view(), name="user_login"),
    path("otp_verify/", views.OTPVerifyView.as_view(), name="otp_verify"),
    path("logout/", views.user_logout, name="user_logout"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.UserProfileUpdateView.as_view(), name="edit_profile"),
    path("profile/edit/pass_change/", views.pass_change, name="pass_change"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset.html",
            email_template_name="password_reset_email.html",
            subject_template_name="password_reset_subject.txt",
            form_class=StyledPasswordResetForm,
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html",
            form_class=StyledSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
