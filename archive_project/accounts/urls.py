from django.contrib import admin
from django.urls import path, include
from . import views
from .views import UserRegistrationView, UserLogoutView, UserProfileUpdateView, OTPVerifyView
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('otp_verify/', OTPVerifyView.as_view(), name='otp_verify'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit', UserProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/edit/pass_change/', views.pass_change, name='pass_change'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]