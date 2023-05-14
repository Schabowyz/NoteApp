from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Note


##################################################     ROUTES     ##################################################

###############     STATIC PAGES     ###############

# Index page for notes
def index(request):
    # If user is not logged in redirects to users
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("users:index"))
    # Gets notes of currently logged user
    return render(request, "notes/index.html", {
        "notes": Note.objects.filter(user_id=request.user.id)
    })

# Information page about the project
def about(request):
    return render(request, "notes/about.html")


###############     FUNCTIONS     ###############

# Add new note in notes page
@login_required
def add(request):
    # Gets info from form and submits it to database
    note = Note(title = request.POST["title"], text = request.POST["text"], user_id = User.objects.get(id = request.user.id))
    note.save()
    messages.success(request, "Your note was successfully added")
    return HttpResponseRedirect(reverse("notes:index"))

# Edit existing note in notes page
@login_required
def edit(request, note_id):
    # Gets info from form and updates db entry
    try:
        note = Note.objects.get(id = note_id)
        # Checks if user is note's owner
        if request.user.username != str(note.user_id):
            messages.success(request, "It's not your note you hacker!")
            return HttpResponseRedirect(reverse("notes:index"))
        note.title = request.POST["title"]
        note.text = request.POST["text"]
        note.save()
        messages.success(request, "Your note was successfully updated")
    # If note doesn't exist
    except ObjectDoesNotExist:
        messages.success(request, "404: That note doesn't exist")
    # Redirects back to notes page
    return HttpResponseRedirect(reverse("notes:index"))

# Delete existing note in notes page
@login_required
def delete(request, note_id):
    # Gets note id and removes it from db
    try:
        note = Note.objects.get(id=note_id)
        # Checks if user is note's owner
        if request.user.username != str(note.user_id):
            messages.success(request, "It's not your note you hacker!")
            return HttpResponseRedirect(reverse("notes:index"))
        note.delete()
        messages.success(request, "Your note was successfully removed")
    # If note doesn't exist
    except ObjectDoesNotExist:
        messages.success(request, "404: That note doesn't exist")
    # Redirects back to notes page
    return HttpResponseRedirect(reverse("notes:index"))