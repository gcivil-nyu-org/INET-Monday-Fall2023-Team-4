from django.urls import path, include
from django.conf import settings
from . import views
from django.conf.urls.static import static
from .views import RegisterView, ChangePasswordView
 
app_name = 'users'
urlpatterns = [
    path('', views.index, name ='index'),
	path('login/', views.Login, name ='login'),
    path('register/', RegisterView.as_view(), name ='register'),
    path('profile/', views.user_profile, name='user_profile'),
    path('password-change/', ChangePasswordView.as_view(), name='password_change'),
]