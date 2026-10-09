from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class AccountTests(TestCase):
    def registration_data(self):
        return {"username": "learner", "password1": "Study!Forest27River", "password2": "Study!Forest27River"}

    def test_registration_login_and_post_logout(self):
        self.assertContains(self.client.get(reverse("register")), "csrfmiddlewaretoken")
        self.assertRedirects(self.client.post(reverse("register"), self.registration_data()), reverse("login"))
        user = get_user_model().objects.get(username="learner")
        self.assertTrue(user.check_password(self.registration_data()["password1"]))
        response = self.client.post(reverse("login"), {"username": "learner", "password": self.registration_data()["password1"]})
        self.assertRedirects(response, reverse("subjects:list"))
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("logout")), reverse("home"))
        self.assertEqual(self.client.get(reverse("subjects:list")).status_code, 302)

    def test_invalid_registration_does_not_create_account(self):
        for changes in [{"password2": "mismatch"}, {"username": ""}, {"password1": "123", "password2": "123"}]:
            data = self.registration_data() | changes
            response = self.client.post(reverse("register"), data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_duplicate_username_is_rejected(self):
        get_user_model().objects.create_user(username="learner")
        response = self.client.post(reverse("register"), self.registration_data())
        self.assertIn("username", response.context["form"].errors)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_invalid_login_and_external_redirect(self):
        self.client.post(reverse("register"), self.registration_data())
        response = self.client.post(reverse("login"), {"username": "learner", "password": "wrong"})
        self.assertTrue(response.context["form"].errors)
        response = self.client.post(reverse("login"), {
            "username": "learner", "password": self.registration_data()["password1"], "next": "https://example.com/",
        })
        self.assertRedirects(response, reverse("subjects:list"))

    def test_registration_login_and_logout_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(reverse("register"), self.registration_data()).status_code, 403)
        self.assertEqual(client.post(reverse("login"), {}).status_code, 403)
        user = get_user_model().objects.create_user(username="existing")
        client.force_login(user)
        self.assertEqual(client.post(reverse("logout")).status_code, 403)
