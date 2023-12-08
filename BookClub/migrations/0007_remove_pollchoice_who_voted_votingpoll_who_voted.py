# Generated by Django 4.2.6 on 2023-12-05 23:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("BookClub", "0006_pollchoice_who_voted"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pollchoice",
            name="who_voted",
        ),
        migrations.AddField(
            model_name="votingpoll",
            name="who_voted",
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
