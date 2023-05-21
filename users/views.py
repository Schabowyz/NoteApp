from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .tokens import account_activation_token


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

def renew_password(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email = request.POST["email"])
            renew_password_mail(request, user)
            return HttpResponseRedirect(reverse("users:index"))
        except User.DoesNotExist:
            messages.error(request, "User doesn't exist")
    return render(request, "users/renew_password.html")

def renew_password_mail(request, user):
    mail_subject = "NoteApp - renew password"
    message = render_to_string("users/renew_password_mail.html", {
        "user": user.username,
        "domain": get_current_site(request).domain,
        "uid": urlsafe_base64_encode(force_bytes(user.username)),
        "token": PasswordResetTokenGenerator().make_token(user),
        "protocol": "https" if request.is_secure() else "http"
    })
    email = EmailMessage(mail_subject, message, to=(user.email,))
    if email.send():
        messages.success(request, "Password renewal email was sent to you, please check your email")
        return True
    else:
        messages.error(request, "Something went wrong")
        return False
    
def newpassword(request, uidb64, token):
    if request.method == "POST":
        username = urlsafe_base64_decode(uidb64).decode()
        print(username)
        user = User.objects.get(username = username)
        user.set_password(request.POST["password1"])
        user.save()
        messages.success(request, "Your password was successfully changed")
        return HttpResponseRedirect(reverse("users:index"))
    return render(request, "users/newpassword.html", {
        "uidb64": uidb64,
        "token": token
    })

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
        # try:
        #     User.objects.get(email=request.POST["email"])
        #     messages.error(request, "Email address already taken")
        #     error = True
        # except ObjectDoesNotExist:
        #     pass
        # Username validation check for availability                                        DODAĆ WALIDACJĘ USERNAME I PASSWORD
        try:
            user = User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password"])
        except IntegrityError:
            messages.error(request, "Login already taken")
            error = True
        # If there was no error raiserd, saves a new user, logs user in and redirects to notes page
        if not error:
            user.is_active = False
            if activate_email(request, user):
                user.save()
                return HttpResponseRedirect(reverse("notes:index"))
            user.delete()
    # Render register page
    return render(request, "users/register.html")

def activate_email(request, user):
    mail_subject = "NoteApp - account activation"
    message = render_to_string("users/activate_account.html", {
        "user": user.username,
        "domain": get_current_site(request).domain,
        "uid": urlsafe_base64_encode(force_bytes(user.username)),
        "token": account_activation_token.make_token(user),
        "protocol": "https" if request.is_secure() else "http"
    })
    email = EmailMessage(mail_subject, message, to=(user.email,))
    if email.send():
        messages.success(request, "Activation email was sent to you. You have to go to your email and confirm the activation")
        return True
    else:
        messages.error(request, "Problem sending message, please check your email")
        return False
        
def activate(request, uidb64, token):
    user = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(username = uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account was succesfully activated, you can log in now")
    else:
        messages.error(request, "Activation link is invalid")
    return HttpResponseRedirect(reverse("users:index"))


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