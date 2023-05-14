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
    path("account", views.account, name="account")
]
