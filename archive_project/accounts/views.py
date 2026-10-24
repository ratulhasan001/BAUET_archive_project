import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import FormView

from posts.models import Post

from .forms import (
    LoginForm,
    OTPForm,
    ProfileUpdateForm,
    RegistrationForm,
    StyledPasswordChangeForm,
)
from .models import Profile, UserOTP
from .tokens import account_activation_token


def send_otp_email(user, otp):
    send_mail(
        subject="Your BAUET Archive login code",
        message=(
            f"Hi {user.get_short_name() or user.username},\n\n"
            f"Your verification code is {otp}. "
            f"It expires in {settings.OTP_EXPIRY_MINUTES} minutes."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


class UserLoginView(auth_views.LoginView):
    template_name = "user_login.html"
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        otp = f"{secrets.randbelow(1_000_000):06d}"
        UserOTP.objects.update_or_create(
            user=user,
            defaults={"otp": otp, "created_at": timezone.now()},
        )
        send_otp_email(user, otp)
        self.request.session["otp_user_id"] = user.id
        messages.info(self.request, f"We sent a 6-digit code to {user.email}.")
        return redirect("otp_verify")

    def form_invalid(self, form):
        messages.error(self.request, "Incorrect username or password.")
        return super().form_invalid(form)


class OTPVerifyView(View):
    template_name = "otp_verify.html"

    def get(self, request):
        if not request.session.get("otp_user_id"):
            return redirect("user_login")
        return render(request, self.template_name, {"form": OTPForm()})

    def post(self, request):
        user_id = request.session.get("otp_user_id")
        if not user_id:
            messages.error(request, "Your session expired. Please log in again.")
            return redirect("user_login")

        form = OTPForm(request.POST)
        if form.is_valid():
            user_otp = UserOTP.objects.filter(
                user_id=user_id, otp=form.cleaned_data["otp"]
            ).select_related("user").first()
            if user_otp and not user_otp.is_expired():
                user = user_otp.user
                user_otp.delete()
                del request.session["otp_user_id"]
                login(request, user)
                messages.success(request, "Welcome back!")
                return redirect("homepage")
            form.add_error("otp", "Invalid or expired code.")
        return render(request, self.template_name, {"form": form})


class UserRegistrationView(FormView):
    template_name = "register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("user_login")

    def form_valid(self, form):
        user = form.save()
        message = render_to_string(
            "acc_active_email.html",
            {
                "user": user,
                "domain": get_current_site(self.request).domain,
                "protocol": "https" if self.request.is_secure() else "http",
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        send_mail(
            subject="Activate your BAUET Archive account",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        messages.success(
            self.request, "Account created. Check your email to activate it before logging in."
        )
        return super().form_valid(form)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        messages.success(request, "Your account is active. You can log in now.")
        return redirect("user_login")

    messages.error(request, "This activation link is invalid or has expired.")
    return redirect("register")


@require_POST
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("user_login")


@login_required
def profile(request):
    Profile.objects.get_or_create(user=request.user)
    posts = (
        Post.objects.filter(authors=request.user)
        .select_related("department")
        .prefetch_related("tags")
        .distinct()
    )
    supervised = (
        Post.objects.filter(supervisors=request.user)
        .select_related("department")
        .prefetch_related("tags")
        .distinct()
    )
    wishlist = getattr(request.user, "wishlist", None)
    saved = wishlist.posts.select_related("department") if wishlist else Post.objects.none()
    return render(
        request,
        "profile.html",
        {"posts": posts, "supervised": supervised, "saved": saved},
    )


class UserProfileUpdateView(LoginRequiredMixin, View):
    template_name = "edit_profile.html"

    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
        return render(request, self.template_name, {"form": form})


@login_required
def pass_change(request):
    if request.method == "POST":
        form = StyledPasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password updated.")
            return redirect("profile")
    else:
        form = StyledPasswordChangeForm(user=request.user)
    return render(request, "pass_change.html", {"form": form})
