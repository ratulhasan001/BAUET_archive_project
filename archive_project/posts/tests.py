import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Profile
from departments.models import Department

from .models import Post

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.dept = Department.objects.create(name="Computer Science and Engineering", slug="cse")
        self.author = User.objects.create_user("author", "author@example.com", "pass12345!")
        self.other = User.objects.create_user("other", "other@example.com", "pass12345!")
        self.supervisor = User.objects.create_user("sup", "sup@example.com", "pass12345!")
        Profile.objects.create(user=self.author, designation="Student")
        self.post = Post.objects.create(
            title="Smart Irrigation",
            content="An IoT based irrigation system.",
            year=2023,
            department=self.dept,
            file=SimpleUploadedFile("report.pdf", b"%PDF-1.4 test"),
            is_approved=True,
        )
        self.post.authors.add(self.author)
        self.post.tags.add("iot")

    def test_home_requires_login(self):
        response = self.client.get(reverse("homepage"))
        self.assertEqual(response.status_code, 302)

    def test_home_filters_and_search(self):
        self.client.force_login(self.other)
        for url in [
            reverse("homepage"),
            reverse("dept_wise_post", args=["cse"]),
            reverse("tag_wise_post", args=["iot"]),
            reverse("search_posts") + "?q=irrigation",
            reverse("search_posts") + "?q=abc&category=year",
            reverse("search_posts") + "?q=author&category=student",
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.get(reverse("search_posts") + "?q=irrigation")
        self.assertContains(response, "Smart Irrigation")

    def test_detail_and_download(self):
        self.client.force_login(self.other)
        self.assertContains(self.client.get(reverse("detail_post", args=[self.post.pk])), "Smart Irrigation")
        response = self.client.get(reverse("download_file", args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])

    def test_unapproved_post_hidden_from_others(self):
        self.post.is_approved = False
        self.post.save()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("detail_post", args=[self.post.pk])).status_code, 404)
        self.client.force_login(self.author)
        self.assertEqual(self.client.get(reverse("detail_post", args=[self.post.pk])).status_code, 200)

    def test_only_owner_can_edit_or_delete(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("edit_post", args=[self.post.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("delete_post", args=[self.post.pk])).status_code, 404)
        self.client.force_login(self.author)
        self.assertEqual(self.client.get(reverse("edit_post", args=[self.post.pk])).status_code, 200)
        self.client.post(reverse("delete_post", args=[self.post.pk]))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_add_post_with_supervisor(self):
        self.client.force_login(self.author)
        response = self.client.post(
            reverse("add_post"),
            {
                "title": "Drone Mapping",
                "content": "Aerial mapping with drones.",
                "department": self.dept.pk,
                "year": 2024,
                "tags": "drones, mapping",
                "supervisor_emails": "sup@example.com",
                "author_emails": "",
                "file": SimpleUploadedFile("drone.pdf", b"%PDF-1.4 drone"),
            },
        )
        self.assertRedirects(response, reverse("profile"))
        post = Post.objects.get(title="Drone Mapping")
        self.assertFalse(post.is_approved)
        self.assertEqual(list(post.authors.all()), [self.author])
        self.assertEqual(list(post.supervisors.all()), [self.supervisor])
        self.assertEqual(post.tags.count(), 2)

    def test_add_post_rejects_unknown_email(self):
        self.client.force_login(self.author)
        response = self.client.post(
            reverse("add_post"),
            {
                "title": "X",
                "content": "Y",
                "department": self.dept.pk,
                "year": 2024,
                "supervisor_emails": "ghost@example.com",
                "file": SimpleUploadedFile("x.pdf", b"x"),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ghost@example.com")

    def test_wishlist_and_comment(self):
        self.client.force_login(self.other)
        self.client.post(reverse("add_to_wishlist", args=[self.post.pk]))
        self.assertContains(self.client.get(reverse("profile")), "Smart Irrigation")
        self.client.post(reverse("detail_post", args=[self.post.pk]), {"body": "Great work"})
        self.assertEqual(self.post.comments.get().name, "other")
