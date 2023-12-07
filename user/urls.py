from django.urls import path, reverse_lazy
from . import views
from .views import ChangePasswordView, ResetPasswordView
from django.contrib.auth import views as auth_views

app_name = "users"
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.user_login, name="login"),
    path("register", views.register, name="register"),
    path("profile", views.user_profile, name="user_profile"),
    path("unsubscribe/<slug:slug>/", views.unsubscribe, name="unsubscribe"),
    path("mute/<slug:slug>/", views.mute, name="mute"),
    path("password-change/", ChangePasswordView.as_view(), name="password_change"),
    path(
        "password-reset/",
        ResetPasswordView.as_view(),
        {
            "post_reset_redirect": "users:password_reset_complete",
        },
        name="password-reset",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="user/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="user/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
