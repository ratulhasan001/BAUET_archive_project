import re

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import UserOTP


class AuthFlowTests(TestCase):
    def test_register_activate_and_login_with_otp(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "rahim",
                "first_name": "Rahim",
                "last_name": "Uddin",
                "email": "rahim@example.com",
                "contact_number": "01700000000",
                "address": "Natore",
                "designation": "Student",
                "dept": "Computer Science and Engineering",
                "password1": "S3cure-pass-123",
                "password2": "S3cure-pass-123",
            },
        )
        self.assertRedirects(response, reverse("user_login"))
        user = User.objects.get(username="rahim")
        self.assertFalse(user.is_active)
        self.assertEqual(user.profile.designation, "Student")

        link = re.search(r"https?://[^/]+(/\S+)", mail.outbox[0].body).group(1)
        self.client.get(link)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        response = self.client.post(
            reverse("user_login"), {"username": "rahim", "password": "S3cure-pass-123"}
        )
        self.assertRedirects(response, reverse("otp_verify"))
        otp = UserOTP.objects.get(user=user).otp
        self.assertIn(otp, mail.outbox[1].body)

        self.client.post(reverse("otp_verify"), {"otp": "000000" if otp != "000000" else "111111"})
        self.assertNotIn("_auth_user_id", self.client.session)

        response = self.client.post(reverse("otp_verify"), {"otp": otp})
        self.assertRedirects(response, reverse("homepage"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_profile_pages_work_without_profile(self):
        admin = User.objects.create_superuser("admin", "admin@example.com", "pass12345!")
        self.client.force_login(admin)
        self.assertEqual(self.client.get(reverse("profile")).status_code, 200)
        self.assertEqual(self.client.get(reverse("edit_profile")).status_code, 200)
        response = self.client.post(
            reverse("edit_profile"),
            {
                "username": "admin",
                "first_name": "Site",
                "last_name": "Admin",
                "email": "admin@example.com",
                "designation": "Lecturer",
                "dept": "Civil Engineering",
            },
        )
        self.assertRedirects(response, reverse("profile"))
        admin.refresh_from_db()
        self.assertEqual(admin.profile.dept, "Civil Engineering")

    def test_logout_requires_post(self):
        user = User.objects.create_user("u", "u@example.com", "pass12345!")
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("user_logout")).status_code, 405)
        self.client.post(reverse("user_logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_password_reset_page(self):
        self.assertEqual(self.client.get(reverse("password_reset")).status_code, 200)
