from django.urls import path

from . import views

app_name = "notes"
urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add, name="add"),
    path("edit/<int:note_id>", views.edit, name="edit"),
    path("delete/<int:note_id>", views.delete, name="delete")
]
