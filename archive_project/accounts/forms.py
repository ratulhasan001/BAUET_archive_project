from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from core.forms import StyledFormMixin

from .constants import DEPARTMENT, DESIGNATION
from .models import Profile


class RegistrationForm(StyledFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(label="Email address")
    contact_number = forms.CharField(label="Contact number", max_length=11)
    address = forms.CharField(max_length=200)
    designation = forms.ChoiceField(choices=DESIGNATION)
    dept = forms.ChoiceField(choices=DEPARTMENT, label="Department")
    image = forms.ImageField(label="Profile photo", required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "contact_number",
            "address",
            "designation",
            "dept",
            "image",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ""

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                designation=self.cleaned_data["designation"],
                dept=self.cleaned_data["dept"],
                contact_number=self.cleaned_data["contact_number"],
                address=self.cleaned_data["address"],
                image=self.cleaned_data.get("image") or "",
            )
        return user


class ProfileUpdateForm(StyledFormMixin, forms.ModelForm):
    contact_number = forms.CharField(label="Contact number", max_length=11, required=False)
    address = forms.CharField(max_length=200, required=False)
    designation = forms.ChoiceField(choices=DESIGNATION)
    dept = forms.ChoiceField(choices=DEPARTMENT, label="Department")
    image = forms.ImageField(label="Profile photo", required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile, _ = Profile.objects.get_or_create(user=self.instance)
        for name in ["contact_number", "address", "designation", "dept"]:
            self.fields[name].initial = getattr(self.profile, name)
        for field in self.fields.values():
            field.help_text = ""

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        taken = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if taken.exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        for name in ["contact_number", "address", "designation", "dept"]:
            setattr(self.profile, name, self.cleaned_data[name])
        if self.cleaned_data.get("image"):
            self.profile.image = self.cleaned_data["image"]
        if commit:
            self.profile.save()
        return user


class LoginForm(StyledFormMixin, AuthenticationForm):
    pass


class OTPForm(StyledFormMixin, forms.Form):
    otp = forms.CharField(
        label="Verification code",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"inputmode": "numeric", "autocomplete": "one-time-code", "autofocus": True}
        ),
    )


class StyledPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    pass


class StyledPasswordResetForm(StyledFormMixin, PasswordResetForm):
    pass


class StyledSetPasswordForm(StyledFormMixin, SetPasswordForm):
    pass
