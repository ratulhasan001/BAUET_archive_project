import re

from django.contrib.auth.models import User
from django.core import mail
from rest_framework.test import APITestCase


class AccountApiTests(APITestCase):
    def test_register_activate_login_logout(self):
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "karim",
                "first_name": "Karim",
                "last_name": "Ahmed",
                "email": "karim@example.com",
                "password": "S3cure-pass-123",
                "confirm_password": "S3cure-pass-123",
                "designation": "Student",
            },
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertFalse(User.objects.get(username="karim").is_active)

        credentials = {"username": "karim", "password": "S3cure-pass-123"}
        self.assertEqual(self.client.post("/api/accounts/login/", credentials).status_code, 400)

        link = re.search(r"http://testserver(/\S+)", mail.outbox[0].body).group(1)
        response = self.client.get(link)
        self.assertIn("activated=1", response["Location"])

        response = self.client.post("/api/accounts/login/", credentials)
        self.assertEqual(response.status_code, 200)
        token = response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        me = self.client.get("/api/accounts/me/")
        self.assertEqual(me.data["username"], "karim")
        self.assertEqual(self.client.patch("/api/accounts/me/", {"address": "Dhaka"}).data["address"], "Dhaka")

        self.assertEqual(self.client.post("/api/accounts/logout/").status_code, 204)
        self.assertEqual(self.client.get("/api/accounts/me/").status_code, 401)

    def test_register_validation(self):
        User.objects.create_user("taken", "taken@example.com", "x")
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "new",
                "first_name": "N",
                "last_name": "U",
                "email": "taken@example.com",
                "password": "S3cure-pass-123",
                "confirm_password": "different-123",
                "designation": "Student",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_profiles_are_read_only(self):
        self.assertEqual(self.client.get("/api/accounts/profiles/").status_code, 200)
        self.assertEqual(self.client.post("/api/accounts/profiles/", {}).status_code, 401)
