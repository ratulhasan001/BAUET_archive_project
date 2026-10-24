import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from departments.models import Department

from .models import Post

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostApiTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.dept = Department.objects.create(name="Civil Engineering", slug="ce")
        self.author = User.objects.create_user("author", "author@example.com", "pass12345!")
        self.other = User.objects.create_user("other", "other@example.com", "pass12345!")
        self.approved = self.make_post("Bridge Design", approved=True)
        self.pending = self.make_post("Soil Testing", approved=False)

    def make_post(self, title, approved):
        post = Post.objects.create(
            title=title,
            content="Abstract",
            year=2024,
            department=self.dept,
            file=SimpleUploadedFile("doc.pdf", b"%PDF"),
            is_approved=approved,
        )
        post.authors.add(self.author)
        return post

    def auth(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_public_list_shows_only_approved(self):
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([p["title"] for p in response.data["results"]], ["Bridge Design"])

    def test_filters(self):
        self.assertEqual(self.client.get("/api/posts/?department=ce").data["count"], 1)
        self.assertEqual(self.client.get("/api/posts/?department=xx").data["count"], 0)
        self.assertEqual(self.client.get("/api/posts/?search=bridge").data["count"], 1)
        self.assertEqual(self.client.get("/api/posts/?search=author").data["count"], 1)
        self.assertEqual(self.client.get("/api/posts/?year=abc").data["count"], 0)

    def test_mine_includes_pending(self):
        self.auth(self.author)
        self.assertEqual(self.client.get("/api/posts/?mine=1").data["count"], 2)

    def test_pending_detail_visibility(self):
        self.assertEqual(self.client.get(f"/api/posts/{self.pending.pk}/").status_code, 404)
        self.auth(self.author)
        self.assertEqual(self.client.get(f"/api/posts/{self.pending.pk}/").status_code, 200)

    def test_create_requires_auth_and_sets_author(self):
        payload = {
            "title": "Traffic Flow",
            "content": "Simulation",
            "year": 2025,
            "department": self.dept.pk,
            "supervisor_emails": "other@example.com",
        }
        self.assertEqual(self.client.post("/api/posts/", payload).status_code, 401)
        self.auth(self.author)
        payload["file"] = SimpleUploadedFile("t.pdf", b"%PDF")
        response = self.client.post("/api/posts/", payload, format="multipart")
        self.assertEqual(response.status_code, 201, response.data)
        post = Post.objects.get(title="Traffic Flow")
        self.assertFalse(post.is_approved)
        self.assertEqual(list(post.authors.all()), [self.author])
        self.assertEqual(list(post.supervisors.all()), [self.other])

    def test_only_managers_can_change(self):
        self.auth(self.other)
        url = f"/api/posts/{self.approved.pk}/"
        self.assertEqual(self.client.patch(url, {"title": "X"}).status_code, 403)
        self.assertEqual(self.client.delete(url).status_code, 403)
        self.auth(self.author)
        self.assertEqual(self.client.patch(url, {"title": "Bridge v2"}).status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 204)
