from django.urls import path

from . import views

app_name = "subjects"
urlpatterns = [
    path("<int:subject_pk>/notes/", views.note_list, name="note_list"),
    path("<int:subject_pk>/notes/new/", views.note_create, name="note_create"),
    path("<int:subject_pk>/notes/<int:note_pk>/", views.note_detail, name="note_detail"),
    path("", views.subject_list, name="list"),
    path("new/", views.subject_create, name="create"),
]
