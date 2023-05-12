from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Note

# Index page for notes
def index(request):
    # If user is not logged in redirects to users
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:index"))
    # Gets notes of currently logged user
    return render(request, "notes/index.html", {
        "notes": Note.objects.filter(user_id=request.user.id)
    })

# Add page for new notes
def add(request):
    # Gets info from form and submits it to database
    if request.method == "POST":
        note = Note(title = request.POST["title"], text = request.POST["text"], user_id = User.objects.get(id = request.user.id))
        note.save()
        return HttpResponseRedirect(reverse("notes:index"))
    return render(request, "notes/add.html")

# Edit page for existing notes
def edit(request, note_id):
    # Gets info from form and updates db entry
    if request.method == "POST":
        note = Note.objects.get(id = note_id)
        note.title = request.POST["title"]
        note.text = request.POST["text"]
        note.save()
        return HttpResponseRedirect(reverse("notes:index"))
    return render(request, "notes/edit.html", {
        "note": Note.objects.get(id = note_id)
    })

# Delete page for existing notes
def delete(request, note_id):
    # Gets note id and removes it from db
    Note.objects.filter(id=note_id).delete()
    return HttpResponseRedirect(reverse("notes:index"))