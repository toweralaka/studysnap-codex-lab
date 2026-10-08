from django.test import SimpleTestCase
from django.urls import reverse


class HomePageTests(SimpleTestCase):
    def test_home_renders_without_database_access(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "StudySnap")
        self.assertContains(response, "Big ideas.")

    def test_home_links_to_available_subject_pages(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, f'href="{reverse("subjects:create")}"')
        self.assertContains(response, f'href="{reverse("subjects:list")}"')

    def test_planned_features_are_labeled(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Available now")
        self.assertContains(response, "Coming later", count=2)
        self.assertContains(response, "Capture your notes")
        self.assertContains(response, "Check your understanding")

