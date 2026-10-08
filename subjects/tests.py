from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Subject


class SubjectModelTests(TestCase):
    def test_name_is_string_representation(self):
        self.assertEqual(str(Subject(name="Biology")), "Biology")

    def test_names_are_required_and_limited_to_100_characters(self):
        for name in ["", "x" * 101]:
            with self.subTest(name=name), self.assertRaises(ValidationError):
                Subject(name=name).full_clean()
        Subject(name="x" * 100).full_clean()

    def test_duplicate_names_are_allowed(self):
        Subject.objects.create(name="Biology")
        Subject.objects.create(name="Biology")
        self.assertEqual(Subject.objects.filter(name="Biology").count(), 2)


class SubjectPageTests(TestCase):
    def test_empty_list_has_create_link(self):
        response = self.client.get(reverse("subjects:list"))
        self.assertContains(response, "No subjects yet")
        self.assertContains(response, reverse("subjects:create"))

    def test_list_displays_subjects_alphabetically(self):
        Subject.objects.create(name="Physics")
        Subject.objects.create(name="Biology")
        response = self.client.get(reverse("subjects:list"))
        self.assertEqual(list(response.context["subjects"].values_list("name", flat=True)), ["Biology", "Physics"])
        self.assertContains(response, "Biology")
        self.assertContains(response, "Physics")

    def test_subject_names_are_html_escaped(self):
        Subject.objects.create(name="<script>alert(1)</script>")
        response = self.client.get(reverse("subjects:list"))
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>")

    def test_create_page_displays_form_and_csrf_token(self):
        response = self.client.get(reverse("subjects:create"))
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertEqual(Subject.objects.count(), 0)

    def test_valid_submission_saves_trimmed_name_and_redirects(self):
        response = self.client.post(reverse("subjects:create"), {"name": "  Chemistry  "})
        self.assertRedirects(response, reverse("subjects:list"))
        self.assertEqual(Subject.objects.get().name, "Chemistry")
        self.assertContains(self.client.get(reverse("subjects:list")), "Chemistry")

    def test_invalid_submission_shows_errors_without_saving(self):
        for data in [{}, {"name": ""}, {"name": "   "}, {"name": "x" * 101}]:
            with self.subTest(data=data):
                response = self.client.post(reverse("subjects:create"), data)
                self.assertEqual(response.status_code, 200)
                self.assertIn("name", response.context["form"].errors)
                self.assertContains(response, 'class="errorlist"')
                self.assertEqual(Subject.objects.count(), 0)

    def test_maximum_length_name_can_be_created(self):
        response = self.client.post(reverse("subjects:create"), {"name": "x" * 100})
        self.assertRedirects(response, reverse("subjects:list"))
        self.assertEqual(Subject.objects.get().name, "x" * 100)

    def test_create_requires_csrf_and_accepts_valid_token(self):
        client = Client(enforce_csrf_checks=True)
        url = reverse("subjects:create")
        self.assertEqual(client.post(url, {"name": "Biology"}).status_code, 403)
        self.assertEqual(Subject.objects.count(), 0)
        client.get(url)
        response = client.post(url, {"name": "Biology", "csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertRedirects(response, reverse("subjects:list"))
        self.assertEqual(Subject.objects.count(), 1)

    def test_unsupported_methods_are_rejected(self):
        self.assertEqual(self.client.post(reverse("subjects:list")).status_code, 405)
        self.assertEqual(self.client.delete(reverse("subjects:create")).status_code, 405)

    def test_subject_pages_link_to_home(self):
        for url in [reverse("subjects:list"), reverse("subjects:create")]:
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), f'href="{reverse("home")}"')
