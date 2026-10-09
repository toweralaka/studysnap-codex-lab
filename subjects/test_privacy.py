from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Note, Subject


class PrivacyTests(TestCase):
    def setUp(self):
        self.alice = get_user_model().objects.create_user(username="alice")
        self.bob = get_user_model().objects.create_user(username="bob")
        self.subject = Subject.objects.create(name="Alice subject", owner=self.alice)
        self.other = Subject.objects.create(name="Bob subject", owner=self.bob)
        # Represents a row created before the ownership migration.
        self.legacy = Subject.objects.create(name="Legacy subject", owner=self.alice)
        Subject.objects.filter(pk=self.legacy.pk).update(owner=None)
        self.note = Note.objects.create(subject=self.subject, title="Private title", body="Private body")
        self.client.force_login(self.alice)

    def url(self, name, subject=None, note=None):
        args = [(subject or self.subject).pk]
        if note:
            args.append(note.pk)
        return reverse("subjects:" + name, args=args)

    def test_subject_lists_are_private_and_hide_ownerless_rows(self):
        for user, expected in [(self.alice, self.subject), (self.bob, self.other)]:
            self.client.force_login(user)
            response = self.client.get(reverse("subjects:list"))
            self.assertEqual(list(response.context["subjects"]), [expected])
            self.assertNotContains(response, "Legacy subject")

    def test_new_subject_owner_cannot_be_spoofed(self):
        response = self.client.post(reverse("subjects:create"), {"name": "New", "owner": self.bob.pk})
        self.assertRedirects(response, reverse("subjects:list"))
        self.assertEqual(Subject.objects.get(name="New").owner, self.alice)

    def test_model_rejects_new_ownerless_subject(self):
        with self.assertRaises(ValidationError):
            Subject.objects.create(name="No owner")

    def test_ownerless_subject_is_preserved(self):
        self.legacy.refresh_from_db()
        self.assertIsNone(self.legacy.owner)
        self.legacy.name = "Renamed legacy"
        self.legacy.save()
        self.assertIsNone(Subject.objects.get(pk=self.legacy.pk).owner)

    def test_anonymous_requests_require_login(self):
        self.client.logout()
        urls = [reverse("subjects:list"), reverse("subjects:create"),
                self.url("note_list"), self.url("note_create"), self.url("note_detail", note=self.note)]
        for url in urls:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), reverse("login") + "?next=" + url)
        self.assertEqual(self.client.post(self.url("note_create"), {"title": "X", "body": "Y"}).status_code, 302)
        self.assertEqual(Note.objects.count(), 1)

    def test_foreign_and_ownerless_subjects_reject_all_note_access(self):
        for subject in [self.other, self.legacy]:
            for name in ["note_list", "note_create", "note_detail"]:
                url = self.url(name, subject, self.note if name == "note_detail" else None)
                with self.subTest(subject=subject.pk, name=name):
                    self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(self.url("note_create", subject), {"title": "X", "body": "Y"}).status_code, 404)
        self.client.force_login(self.bob)
        self.assertEqual(self.client.get(self.url("note_detail", note=self.note)).status_code, 404)
        self.assertEqual(Note.objects.count(), 1)

    def test_note_must_match_subject_url(self):
        second = Subject.objects.create(name="Second", owner=self.alice)
        self.assertEqual(self.client.get(self.url("note_detail", second, self.note)).status_code, 404)

    def test_owned_notes_can_be_listed_viewed_and_created(self):
        self.assertContains(self.client.get(self.url("note_list")), "Private title")
        self.assertContains(self.client.get(self.url("note_detail", note=self.note)), "Private body")
        response = self.client.post(self.url("note_create"), {
            "title": "  New title  ", "body": "  New body  ", "subject": self.other.pk,
        })
        note = Note.objects.get(title="New title")
        self.assertEqual(note.subject, self.subject)
        self.assertEqual(note.body, "New body")
        self.assertIsNotNone(note.created_at)
        self.assertIsNotNone(note.updated_at)
        self.assertRedirects(response, self.url("note_detail", note=note))

    def test_title_and_body_are_required(self):
        for data in [{}, {"title": "Title"}, {"body": "Body"},
                     {"title": " ", "body": "Body"}, {"title": "Title", "body": " "},
                     {"title": "x" * 201, "body": "Body"}]:
            with self.subTest(data=data):
                response = self.client.post(self.url("note_create"), data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
                self.assertContains(response, 'class="errorlist"')
        self.assertEqual(Note.objects.count(), 1)

    def test_note_content_is_escaped(self):
        self.note.title = "<script>title</script>"
        self.note.body = "<script>body</script>"
        self.note.save()
        response = self.client.get(self.url("note_detail", note=self.note))
        self.assertContains(response, "&lt;script&gt;title&lt;/script&gt;")
        self.assertContains(response, "&lt;script&gt;body&lt;/script&gt;")
        self.assertNotContains(response, "<script>")
        self.assertContains(self.client.get(self.url("note_list")), "&lt;script&gt;title&lt;/script&gt;")

    def test_note_creation_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.alice)
        url = self.url("note_create")
        self.assertEqual(client.post(url, {"title": "X", "body": "Y"}).status_code, 403)
        client.get(url)
        response = client.post(url, {"title": "X", "body": "Y", "csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 2)

    def test_note_pages_reject_unsupported_methods(self):
        self.assertEqual(self.client.post(self.url("note_list")).status_code, 405)
        self.assertEqual(self.client.post(self.url("note_detail", note=self.note)).status_code, 405)
        self.assertEqual(self.client.delete(self.url("note_create")).status_code, 405)
