from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# class UserProfile(models.Model):

#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     bio = models.TextField()

#     def __str__(self):
#         return self.user.username

#     def get_absolute_url(self):
#         return reverse("_detail", kwargs={"pk": self.pk})
