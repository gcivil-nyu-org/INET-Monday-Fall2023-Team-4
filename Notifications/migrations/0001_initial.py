# Generated by Django 4.2.6 on 2023-12-05 19:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("BookClub", "0004_bookclub_silencenotification"),
    ]

    operations = [
        migrations.CreateModel(
            name="TransferOwnershipNotif",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_read", models.BooleanField(default=False)),
                ("message", models.TextField()),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        max_length=30, verbose_name=["accepted", "pending", "declined"]
                    ),
                ),
                (
                    "book_club",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transferred_book_club",
                        to="BookClub.bookclub",
                    ),
                ),
                (
                    "new_owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="new_admin",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "original_owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="old_admin",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["date_created"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="BookClubUpdatesNotif",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_read", models.BooleanField(default=False)),
                ("message", models.TextField()),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("fields_changed", models.TextField()),
                (
                    "book_club",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="updated_book_club",
                        to="BookClub.bookclub",
                    ),
                ),
                (
                    "receiving_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="receiving_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["date_created"],
                "abstract": False,
            },
        ),
    ]
