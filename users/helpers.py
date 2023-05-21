from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email



def register_validate(request):
    error = False

    # Email validation and check for availability
    email = request.POST["email"]
    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, "Ivalid email address")
        error = True
    try:
        User.objects.get(email=email)
        messages.error(request, "Email address already taken")
        error = True
    except ObjectDoesNotExist:
        pass

    # Username validation check for availability
    username = request.POST["username"]
    if len(username) < 4 or len(username) > 20:
        messages.error(request, "Username must be between 4 and 20 characters long")
    try:
        User.objects.get(username=username)
        messages.error(request, "Username already taken")
        error = True
    except ObjectDoesNotExist:
        pass
    
    # Password validation
    password = request.POST["password"]
    if password_check(request):
        error = True

    # Creates a new user if there was no error, otherwise returns false
    if error == False:
        return User.objects.create_user(username, email, password)
    return False


def password_check(request):
    error = False

    # Password validation
    password = request.POST["password"]
    if password != request.POST["repeat"]:
        messages.error(request, "Passwords don't match")
        error = True
    try:
        validate_password(password)
    except ValidationError:
        messages.error(request, "Password doesn't meet the requirements")
        error = True

    # Returns error
    return error