from django.urls import path
from Subscription.views import toggle_club_join

app_name = "Subscription"

urlpatterns = [
    path(
        "toggle-join/<int:user_pk>/<int:bookclub_pk>/",
        toggle_club_join,
        name="toggle-join",
    ),
]
