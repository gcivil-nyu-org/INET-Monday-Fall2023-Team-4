# Generated by Django 4.2.6 on 2023-12-06 02:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("BookClub", "0007_remove_pollchoice_who_voted_votingpoll_who_voted"),
    ]

    operations = [
        migrations.AddField(
            model_name="pollchoice",
            name="user_voted",
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
