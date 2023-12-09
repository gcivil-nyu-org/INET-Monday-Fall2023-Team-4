from django.shortcuts import render, redirect, get_object_or_404
from libraries.models import Library
from BookClub.models import BookClub, VotingPoll, PollChoice
from Notifications.models import TransferOwnershipNotif, BookClubUpdatesNotif
from books.models import Book
from django.contrib import messages
from .forms import BookClubForm, BookClubEditForm, BookClubVotingForm
from django.conf import settings
from django.core.mail import send_mail
from smtplib import SMTPException
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Q
from books.utils import get_book_cover


def voting_form(request, slug):
    bc = BookClub.objects.get(id=slug)
    context = {}
    if bc.polls != 0:
        poll = VotingPoll.objects.get(id=bc.polls)
        choices = poll.choices.all()
        context = {
            "previous_form": True,
            "who_voted": poll.who_voted.all(),
            "choice1": {"name": choices[0].name, "votes": choices[0].votes},
            "choice2": {"name": choices[1].name, "votes": choices[1].votes},
            "choice3": {"name": choices[2].name, "votes": choices[2].votes},
        }
    if request.method == "POST":
        if "submit" in request.POST:
            form = BookClubVotingForm(request.POST)
            if form.is_valid():
                bc = BookClub.objects.get(id=slug)
                poll = VotingPoll.objects.create(
                    poll_set=True, name="Voting Poll for " + bc.name
                )
                ch1 = PollChoice.objects.create(
                    name=form.cleaned_data["book1"], votes=0
                )
                ch1.save()
                poll.choices.add(ch1)
                ch2 = PollChoice.objects.create(
                    name=form.cleaned_data["book2"], votes=0
                )
                ch2.save()
                poll.choices.add(ch2)
                ch3 = PollChoice.objects.create(
                    name=form.cleaned_data["book3"], votes=0
                )
                ch3.save()
                poll.choices.add(ch3)
                if bc.polls != 0:
                    VotingPoll.objects.filter(id=bc.polls).delete()
                poll.save()
                bc.polls = poll.id
                bc.save()
                return redirect("details", slug=slug)
    return render(request, "voting.html", context)


def checkIfAllowedToSubscribe(bookclub, request):
    if bookclub.libraryId.NYU == "0" or (
        bookclub.libraryId.NYU == "1" and request.user.status == "nyu"
    ):
        bookclub.members.add(request.user)
    else:
        messages.error(
            request, "You must be a NYU student to subscribe to this book club"
        )


def getBookInfo(currentBook, currentAuthor, currentBookIsbn):
    book_list = Book.objects.filter(
        Q(title__icontains=currentBook) | Q(isbn__exact=currentBookIsbn)
    )

    if len(book_list) == 0:
        book = Book.objects.create(
            title=currentBook, author=currentAuthor, isbn=currentBookIsbn
        )
        return book
    else:
        return book_list[0]


def book_club_details(request, slug):
    bc = BookClub.objects.get(id=slug)
    book = getBookInfo(bc.currentBook, bc.currentAuthor, bc.currentBookIsbn)
    book_cover = get_book_cover(book)
    average = book.average_rating
    poll = None
    if bc.polls != 0:
        poll = VotingPoll.objects.get(id=bc.polls)
    context = {
        "bookclub": bc,
        "member_count": bc.members.all().count(),
        "subscribed": bc.members.contains(request.user)
        if request.user.is_authenticated
        else False,
        "voting_poll": poll,
        "choices": poll.choices.all() if poll else None,
        "amount_voted": poll.get_all_votes() if poll else None,
        "voted": poll.did_vote(request.user) if poll else None,
        "is_member": True if request.user in bc.members.all() else False,
        "book": book,
        "book_cover": book_cover,
        "average_rating": average,
    }
    if request.method == "POST":
        if "subscribe" in request.POST:
            checkIfAllowedToSubscribe(bc, request)
            return redirect("details", slug=slug)
        elif "unsubscribe" in request.POST:
            if poll and poll.did_vote(request.user):
                poll.remove_user_from_poll(request.user)
            bc.members.remove(request.user)
            return redirect("details", slug=slug)
        elif "choice1" in request.POST:
            selected_choice = poll.choices.all()[0]
            selected_choice.votes += 1
            selected_choice.user_voted.add(request.user)
            selected_choice.save()
            poll.who_voted.add(request.user)
            return redirect("details", slug=slug)
        elif "choice2" in request.POST:
            selected_choice = poll.choices.all()[1]
            selected_choice.votes += 1
            selected_choice.user_voted.add(request.user)
            selected_choice.save()
            poll.who_voted.add(request.user)
            return redirect("details", slug=slug)
        elif "choice3" in request.POST:
            selected_choice = poll.choices.all()[2]
            selected_choice.votes += 1
            selected_choice.user_voted.add(request.user)
            selected_choice.save()
            poll.who_voted.add(request.user)
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
            return redirect("error_page")

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
    notif = ""
    index = 0
    list_bullet = "{index}.\t{bc_name}"
    result = "{new_data}. \n"
    notif_r = "{new_data}--!!--"
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
        notif += bc_name + new_line + notif_r.format(new_data=v)
        content += (
            list_bullet.format(index=index, bc_name=bc_name)
            + new_line
            + result.format(new_data=v)
        )
    return content, notif


def edit_book_club(request, book_club_id):
    book_club = get_object_or_404(BookClub, id=book_club_id)
    original_bc_name = book_club.name

    if request.user != book_club.admin:
        return redirect("error_page")

    if request.method == "POST":
        form = BookClubEditForm(request.POST, instance=book_club)
        if not form.has_changed():
            form = BookClubEditForm(instance=book_club)
            messages.error(request, "Please modify the fields before saving!")
            return render(
                request, "bookclub_edit.html", {"form": form, "book_club": book_club}
            )
        if form.is_valid():
            if "new_admin" in request.POST:
                new_admin = form.cleaned_data["new_admin"]
                if new_admin != book_club.admin:
                    transferReq = TransferOwnershipNotif(
                        original_owner=request.user,
                        new_owner=new_admin,
                        book_club=book_club,
                        status="pending",
                        date_created=datetime.now(),
                    )
                    transferReq.save()
            form.save()
            fields_changed = form.changed_data
            changed_fields_and_data = {}
            for i in fields_changed:
                if i == "new_admin":
                    continue
                changed_fields_and_data[i] = request.POST[i]
            if changed_fields_and_data:
                try:
                    content, notif = get_email_content(
                        changed_fields_and_data, original_bc_name
                    )
                    bc_members = book_club.members.all()
                    for mem in bc_members:
                        if not book_club.silenceNotification.contains(mem):
                            updateNotif = BookClubUpdatesNotif(
                                safe_to_delete=True,
                                date_created=datetime.now(),
                                receiving_user=mem,
                                book_club=book_club,
                                fields_changed=notif,
                            )
                            updateNotif.save()

                    email_list = [
                        mem.email
                        for mem in bc_members
                        if not book_club.silenceNotification.contains(mem)
                    ]

                    subject, content, from_email = (
                        "Check new updates from your book club!",
                        content,
                        settings.EMAIL_HOST_USER,
                    )
                    send_mail(
                        subject, content, from_email, email_list, fail_silently=False
                    )
                except SMTPException:
                    messages.error(request, "Failed to notify members of your updates")

            return redirect("details", slug=book_club.id)
    else:
        form = BookClubEditForm(
            instance=book_club, initial={"new_admin": book_club.admin}
        )

    return render(request, "bookclub_edit.html", {"form": form, "book_club": book_club})


def error_page(request):
    return render(request, "bookclub_error_page.html")


@login_required
def delete_book_club(request):
    if request.method == "POST":
        book_club_id = request.POST.get("book_club_id")
        book_club = get_object_or_404(BookClub, id=book_club_id)

        if request.user == book_club.admin:
            member_emails = [member.email for member in book_club.members.all()]

            book_club.delete()
            messages.success(request, "Book club deleted successfully.")

            subject = "Book Club Deletion Notification"
            message = f"The book club '{book_club.name}' has been deleted by the admin."
            from_email = settings.EMAIL_HOST_USER

            try:
                send_mail(
                    subject, message, from_email, member_emails, fail_silently=False
                )
            except SMTPException:
                messages.error(request, "Failed to notify members about the deletion.")

            return redirect("deletion_confirmation")

        else:
            messages.error(request, "You are not authorized to delete this book club.")
            return redirect("error_page")


def deletion_confirmation(request):
    return render(request, "bookclub_deletion.html")
