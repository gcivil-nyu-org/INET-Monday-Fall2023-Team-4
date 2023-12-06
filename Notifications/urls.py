from django.urls import path
from Notifications.views import NotificationListView

app_name = "notifications"

urlpatterns = [path("", NotificationListView.as_view(), name="notifications")]
