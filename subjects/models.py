from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="subjects", null=True, blank=True,
    )

    class Meta:
        ordering = ["name", "pk"]

    def save(self, *args, **kwargs):
        # Null ownership is retained only for subjects predating this feature.
        if self._state.adding and self.owner_id is None:
            raise ValidationError({"owner": "New subjects must have an owner."})
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Note(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return self.title
