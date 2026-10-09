from django import forms

from .models import Note, Subject


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name"]


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "body"]
