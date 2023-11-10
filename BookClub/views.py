from django.shortcuts import render, redirect, get_object_or_404
from .models import BookClub
from user.models import CustomUser
from .forms import BookClubForm, BookClubEditForm
from django.conf import settings
from django.core.mail import send_mass_mail, send_mail
from smtplib import SMTPException
from django.contrib import messages

def create_book_club(request):
    form = BookClubForm
    return render(request, "bookclub.html", {"form": form})


def get_email_content(fields_changed, bc_name):
    # input is dict of fields and data changed by form, if name is changed, take old name as bc_name
    content = "Here are the latest updates from " + bc_name + "\n\r"
    index = 0
    list_bullet = "{index}.\t{bc_name}"
    result = "{new_data}. \n"
    for k, v in fields_changed.items():
        index += 1
        if k == "name":
            new_line = " changed its name to "
        elif k == "description":
            new_line = " updated its description - "
        elif k == "currentBook":
            new_line = " is currently reading "
        elif k == "meetingDay":
            new_line = " changed its meeting day to "
        elif k == "meetingStartTime":
            new_line = " updated its meeting time to start from "
        elif k == "meetingEndTime":
            new_line = " updated its meeting time to end at "
        elif k == "meetingOccurence":
            new_line = " updated its meeting occurrence to "
        elif k == "libraryId":
            new_line = " is now associated with "
        else:
            new_line = " has a new admin: "
        content += (
            list_bullet.format(index=index, bc_name=bc_name)
            + new_line
            + result.format(new_data=v)
        )
    return content


def edit_book_club(request, book_club_id):
    book_club = get_object_or_404(BookClub, id=book_club_id)
    original_bc_name = book_club.name

    if request.method == "POST":
        form = BookClubEditForm(request.POST, instance=book_club)
        if form.is_valid():
            new_admin = form.cleaned_data["admin"]
            if new_admin not in book_club.members.all():
                book_club.members.add(new_admin)
            form.save()
            fields_changed = form.changed_data
            changed_fields_and_data = {}
            for i in fields_changed:
                if i == "admin":
                    new_admin = get_object_or_404(CustomUser, id=request.POST[i])
                    changed_fields_and_data[i] = new_admin.first_name
                    continue
                changed_fields_and_data[i] = request.POST[i]
            try:
                bc_members = book_club.members.all()
                email_list = [mem.email for mem in bc_members]
                content = get_email_content(changed_fields_and_data, original_bc_name)
                subject, content, from_email = ("Check new updates from your book club!", 
                                get_email_content(changed_fields_and_data, original_bc_name), 
                                settings.EMAIL_HOST_USER,)
                send_mail(subject, content, from_email, email_list, fail_silently=False)
            except SMTPException as e:
                print(e)
                messages.error(request, "Failed to notify members of your updates")
            
            return redirect("book_club_detail", book_club_id=book_club.id)
    else:
        form = BookClubEditForm(instance=book_club)

    return render(request, "bookclub_edit.html", {"form": form, "book_club": book_club})


def book_club_detail(request, book_club_id):
    book_club = get_object_or_404(BookClub, id=book_club_id)

    context = {
        "book_club": book_club,
    }

    return render(request, "bookclub_detail.html", context)
