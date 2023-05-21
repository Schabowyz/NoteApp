from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("email", views.email, name="email"),
    path("password", views.password, name="password"),
    path("delete", views.delete, name="delete"),
    path("account", views.account, name="account"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path("renew_password", views.renew_password, name="renew_password"),
    path("newpassword/<uidb64>/<token>", views.newpassword, name="newpassword")
    ]
