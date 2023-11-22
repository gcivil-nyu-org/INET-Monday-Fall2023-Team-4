from django.shortcuts import render, redirect, get_object_or_404
from libraries.models import Library
from .models import BookClub
from django.contrib import messages
from django.http import HttpResponseForbidden
from user.models import CustomUser
from .forms import BookClubForm, BookClubEditForm
from django.conf import settings
from django.core.mail import send_mail
from smtplib import SMTPException
from django.contrib.auth.decorators import login_required


def checkIfAllowedToSubscribe(bookclub, request):
    if bookclub.libraryId.NYU == "0" or (
        bookclub.libraryId.NYU == "1" and request.user.status == "nyu"
    ):
        bookclub.members.add(request.user)
    else:
        messages.error(
            request, "You must be a NYU student to subscribe to this book club"
        )


def book_club_details(request, slug):
    bc = BookClub.objects.get(id=slug)
    context = {
        "bookclub": bc,
        "member_count": bc.members.all().count(),
        "subscribed": bc.members.contains(request.user)
        if request.user.is_authenticated
        else False,
    }
    if request.method == "POST":
        if "subscribe" in request.POST:
            checkIfAllowedToSubscribe(bc, request)
            return redirect("details", slug=slug)
        elif "unsubscribe" in request.POST:
            bc.members.remove(request.user)
            return redirect("details", slug=slug)
    return render(request, "details.html", context)


@login_required
def create_book_club(request):
    library_id = request.GET.get("libraryId") or request.POST.get("libraryId")
    library = Library.objects.get(id=int(library_id))
    form = BookClubForm(request.POST or None)
    if request.method == "POST":
        if request.user.status == "nyu" and library.NYU == "1":
            if form.is_valid():
                book_club = form.save(commit=False)
                book_club.admin = request.user
                book_club.libraryId = library
                book_club.save()
                book_club.members.add(request.user)

                return redirect("details", slug=book_club.id)
        elif request.user.status != "nyu" and library.NYU == "1":
            error_message = (
                "You are not allowed to create a book club for NYU libraries."
            )
            return HttpResponseForbidden(error_message)

        else:
            if form.is_valid():
                library = Library.objects.get(id=int(library_id))
                book_club = form.save(commit=False)
                book_club.admin = request.user
                book_club.libraryId = library
                book_club.save()
                book_club.members.add(request.user)

                return redirect("details", slug=book_club.id)
    else:
        form = BookClubForm()
    return render(request, "bookclub.html", {"form": form})


def get_email_content(fields_changed, bc_name):
    # input is dict of fields and data changed by form
    # if name is changed, take old name as bc_name
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

    if request.user != book_club.admin:
        return HttpResponseForbidden(
            "You don't have permission to edit this Book Club."
        )

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
                email_list = [
                    mem.email
                    for mem in bc_members
                    if not book_club.silenceNotification.contains(mem)
                ]
                print(email_list)
                content = get_email_content(changed_fields_and_data, original_bc_name)
                subject, content, from_email = (
                    "Check new updates from your book club!",
                    get_email_content(changed_fields_and_data, original_bc_name),
                    settings.EMAIL_HOST_USER,
                )
                send_mail(subject, content, from_email, email_list, fail_silently=False)
            except SMTPException:
                messages.error(request, "Failed to notify members of your updates")

            return redirect("details", slug=book_club.id)
    else:
        form = BookClubEditForm(instance=book_club)

    return render(request, "bookclub_edit.html", {"form": form, "book_club": book_club})
