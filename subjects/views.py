from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from .forms import NoteForm, SubjectForm
from .models import Subject


@login_required
@require_safe
def subject_list(request):
    subjects = Subject.objects.filter(owner=request.user)
    return render(request, "subjects/list.html", {"subjects": subjects})


@login_required
@require_http_methods(["GET", "POST"])
def subject_create(request):
    form = SubjectForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        subject = form.save(commit=False)
        subject.owner = request.user
        subject.save()
        return redirect("subjects:list")
    return render(request, "subjects/form.html", {"form": form})


def owned_subject(request, subject_pk):
    return get_object_or_404(Subject, pk=subject_pk, owner=request.user)


@login_required
@require_safe
def note_list(request, subject_pk):
    subject = owned_subject(request, subject_pk)
    return render(request, "subjects/note_list.html", {"subject": subject, "notes": subject.notes.all()})


@login_required
@require_http_methods(["GET", "POST"])
def note_create(request, subject_pk):
    subject = owned_subject(request, subject_pk)
    form = NoteForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        note = form.save(commit=False)
        note.subject = subject
        note.save()
        return redirect("subjects:note_detail", subject_pk=subject.pk, note_pk=note.pk)
    return render(request, "subjects/note_form.html", {"subject": subject, "form": form})


@login_required
@require_safe
def note_detail(request, subject_pk, note_pk):
    subject = owned_subject(request, subject_pk)
    note = get_object_or_404(subject.notes, pk=note_pk)
    return render(request, "subjects/note_detail.html", {"subject": subject, "note": note})
