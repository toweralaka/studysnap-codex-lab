from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from .forms import SubjectForm
from .models import Subject


@require_safe
def subject_list(request):
    return render(request, "subjects/list.html", {"subjects": Subject.objects.all()})


@require_http_methods(["GET", "POST"])
def subject_create(request):
    form = SubjectForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("subjects:list")
    return render(request, "subjects/form.html", {"form": form})
