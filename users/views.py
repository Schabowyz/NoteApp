from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# Create your views here.
def index(request):
    return render(request, "users/index.html")

def login_view(request):
    # If form is submitted gets form data and checks it
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # If user was autenthicated correctly, redirects to notes page
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("notes:index"))
        # If user wasnt auth correctly
    # Renders login page
    return render(request, "users/login.html")

def logout_view(request):
    # Logs out and redirects to index page
    logout(request)
    return HttpResponseRedirect(reverse("users:index"))

def register(request):
    if request.method == "POST":
        user = User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password"])
        user.save()
        login(request, user)
        return HttpResponseRedirect(reverse("notes:index"))
    return render(request, "users/register.html")

def email(request):
    # Updates users email and redirects to profile
    if request.method == "POST":
        user = User.objects.get(id = request.user.id)
        user.email = request.POST["email"]
        user.save()
        return HttpResponseRedirect(reverse("users:index"))
    return render(request, "users/email.html")

def password(request):
    # Checks if passwords match, then updates user password and redirects to profile
    if request.method == "POST":
        if request.POST["password"] == request.POST["repeat"]:
            user = User.objects.get(id = request.user.id)
            user.set_password(request.POST["password"])
            user.save()
            update_session_auth_hash(request, user)
            return HttpResponseRedirect(reverse("users:index"))
    return render(request, "users/password.html")

def delete(request):
    # Checks if password match, then deletes users account
    if request.method == "POST":
        if check_password(request.POST["password"], request.user.password):
            User.objects.get(id = request.user.id).delete()
            logout(request)
            return HttpResponseRedirect(reverse("users:index"))
    return render(request, "users/delete.html")