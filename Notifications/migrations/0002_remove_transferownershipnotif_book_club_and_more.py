# Generated by Django 4.2.6 on 2023-12-05 20:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Notifications", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transferownershipnotif",
            name="book_club",
        ),
        migrations.RemoveField(
            model_name="transferownershipnotif",
            name="new_owner",
        ),
        migrations.RemoveField(
            model_name="transferownershipnotif",
            name="notification_ptr",
        ),
        migrations.RemoveField(
            model_name="transferownershipnotif",
            name="original_owner",
        ),
        migrations.DeleteModel(
            name="BookClubUpdatesNotif",
        ),
        migrations.DeleteModel(
            name="Notification",
        ),
        migrations.DeleteModel(
            name="TransferOwnershipNotif",
        ),
    ]
