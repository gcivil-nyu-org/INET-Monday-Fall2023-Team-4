from django.urls import path
from . import views
from .views import ChangePasswordView

app_name = "users"
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.user_login, name="login"),
    path("register/", views.register, name="register"),
    path("profile/", views.user_profile, name="user_profile"),
    path("password-change/", ChangePasswordView.as_view(), name="password_change"),
]
