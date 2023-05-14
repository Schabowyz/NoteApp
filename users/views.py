from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("notes:index"))
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
            messages.success(request, "You were successfully logged in")
            return HttpResponseRedirect(reverse("notes:index"))
        messages.success(request, "Invalid login credentials")
        return render(request, "users/login.html")
    # Renders login page
    return render(request, "users/login.html")

@login_required
def logout_view(request):
    # Logs out and redirects to index page
    logout(request)
    messages.success(request, "You were successfully logged out")
    return HttpResponseRedirect(reverse("users:index"))

def register(request):
    if request.method == "POST":
        user = User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password"])
        user.save()
        login(request, user)
        messages.success(request, "You were successfully registered")
        return HttpResponseRedirect(reverse("notes:index"))
    return render(request, "users/register.html")

@login_required
def email(request):
    # Updates users email and redirects to profile
    if request.user.username == "demo_user":
        messages.success(request, "You can't change demo user's credentials. If you wish to use this feature, you have to create your own account")
        return HttpResponseRedirect(reverse("users:account"))
    user = User.objects.get(id = request.user.id)
    user.email = request.POST["email"]
    user.save()
    messages.success(request, "Your email was succesfully updated")
    return HttpResponseRedirect(reverse("users:account"))

@login_required
def password(request):
    # Checks if passwords match, then updates user password and redirects to profile
    if request.user.username == "demo_user":
        messages.success(request, "You can't change demo user's credentials. If you wish to use this feature, you have to create own your own account")
        return HttpResponseRedirect(reverse("users:account"))
    if  authenticate(request, username=request.user.username, password=request.POST["old_password"]):
        if request.POST["password"] == request.POST["repeat"]:
            user = User.objects.get(id = request.user.id)
            user.set_password(request.POST["password"])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated")
            return HttpResponseRedirect(reverse("users:account"))
    messages.success(request, "Invalid password")
    return HttpResponseRedirect(reverse("users:account"))

@login_required
def delete(request):
    # Checks if password match, then deletes users account
    if request.user.username == "demo_user":
        messages.success(request, "You can't remove demo user's account. If you wish to use this feature, you have to create own your own account")
        return HttpResponseRedirect(reverse("users:account"))
    if check_password(request.POST["password"], request.user.password):
        User.objects.get(id = request.user.id).delete()
        logout(request)
        messages.success(request, "Your account was successfully deleted")
        return HttpResponseRedirect(reverse("users:index"))

@login_required
def account(request):
    return render(request, "users/account.html")