from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


##################################################     ROUTES     ##################################################

###############     STATIC PAGES     ###############

# Index page - if user isn't logged, render index page, otherwise redirect to notes page
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("notes:index"))
    return render(request, "users/index.html")

# User's account page with all the users information
@login_required
def account(request):
    return render(request, "users/account.html")


###############     FUNCTIONAL PAGES     ###############

# Login page
def login_view(request):
    # If form is submitted gets form data and checks it
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # If user was autenthicated correctly, logs user in and redirects to notes page, otherwise rerenders login page with error message
        if user:
            login(request, user)
            messages.success(request, "You were successfully logged in")
            return HttpResponseRedirect(reverse("notes:index"))
        messages.error(request, "Invalid login credentials")
    # Renders login page
    return render(request, "users/login.html")

# Register page
def register(request):
    # If form is submitted checks forms information
    if request.method == "POST":
        error = False
        # Email validation and check for availability
        try:
            validate_email(request.POST["email"])
        except ValidationError:
            messages.error(request, "Ivalid email address")
            error = True
        try:
            User.objects.get(email=request.POST["email"])
            messages.error(request, "Email address already taken")
            error = True
        except ObjectDoesNotExist:
            pass
        # Username validation check for availability                                        DODAĆ WALIDACJĘ USERNAME I PASSWORD
        try:
            user = User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password"])
        except IntegrityError:
            messages.error(request, "Login already taken")
            error = True
        # If there was no error raiserd, saves a new user, logs user in and redirects to notes page
        if not error:
            user.save()
            login(request, user)
            messages.success(request, "You were successfully registered")
            return HttpResponseRedirect(reverse("notes:index"))
    # Render register page
    return render(request, "users/register.html")


###############     FUNCTIONS     ###############

# Logout
@login_required
def logout_view(request):
    # Logs out and redirects to index page
    logout(request)
    messages.success(request, "You were successfully logged out")
    return HttpResponseRedirect(reverse("users:index"))

# Email change in account page
@login_required
def email(request):
    # Checks if user is not a demo user
    if request.user.username == "demo_user":
        messages.error(request, "You can't change demo user's credentials. If you wish to use this feature, you have to create your own account")
        return HttpResponseRedirect(reverse("users:account"))
    # Checks if email is valid and if email is available
    error = False
    try:
        validate_email(request.POST["email"])
    except ValidationError:
        messages.error(request, "Invalid email adress")
        error = True
    try:
        if request.user.email != request.POST["email"]:
            User.objects.get(email=request.POST["email"])
            messages.error(request, "Email address already taken")
            error = True
    except ObjectDoesNotExist:
        pass
    # If no error was raised sets new email and redirects back to account page
    if not error:
        user = User.objects.get(id = request.user.id)
        user.email = request.POST["email"]
        user.save()
        messages.success(request, "Your email was succesfully updated")
    return HttpResponseRedirect(reverse("users:account"))

# Password check in account page
@login_required
def password(request):
    # Checks if user is not a demo user
    if request.user.username == "demo_user":
        messages.error(request, "You can't change demo user's credentials. If you wish to use this feature, you have to create own your own account")
        return HttpResponseRedirect(reverse("users:account"))
    # Checks if old password is correct, then checks if new passwords match, if it's ok saves new pw and returns to account page                        DODAĆ WALIDACJĘ PASSWORD
    if authenticate(request, username=request.user.username, password=request.POST["old_password"]):
        if request.POST["password"] == request.POST["repeat"]:
            user = User.objects.get(id = request.user.id)
            user.set_password(request.POST["password"])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated")
            return HttpResponseRedirect(reverse("users:account"))
    # If something is wrong returns to account page
    messages.error(request, "Invalid password")
    return HttpResponseRedirect(reverse("users:account"))

# Account delete in account page
@login_required
def delete(request):
    # Checks if user is not a demo user
    if request.user.username == "demo_user":
        messages.error(request, "You can't remove demo user's account. If you wish to use this feature, you have to create own your own account")
        return HttpResponseRedirect(reverse("users:account"))
    # Checks if password match, then deletes users account and redirects user to index page
    if check_password(request.POST["password"], request.user.password):
        User.objects.get(id = request.user.id).delete()
        logout(request)
        messages.success(request, "Your account was successfully deleted")
        return HttpResponseRedirect(reverse("users:index"))