from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import UserRegisterForm, ValidateForm, UpdateUserForm
from django.core.mail import send_mail
from django.urls import reverse_lazy
from smtplib import SMTPException
from django.core.exceptions import ObjectDoesNotExist
from BookClub.models import BookClub, VotingPoll
import time
import random
import string


def index(request):
    bookclubs_ids = BookClub.members.through.objects.filter(
        customuser_id=request.user.id
    )
    bookclubs = []
    for mapping in bookclubs_ids:
        bookclubs.append(BookClub.objects.get(id=mapping.bookclub_id))
    return render(
        request,
        "user/index.html",
        {"title": "index", "subscriptions": bookclubs, "isfrontpage": True},
    )


def mute(request, slug):
    if request.user:
        bc = BookClub.objects.get(id=slug)
        if request.method == "POST":
            if "mute" in request.POST:
                bc.silenceNotification.add(request.user)
                messages.info(
                    request,
                    "Notifications muted. "
                    + "You will no longer recieve notifications from this book club.",
                )
            elif "unmute" in request.POST:
                bc.silenceNotification.remove(request.user)
                messages.info(
                    request,
                    "Notification unmuted. You will now recieve notifications.",
                )
    else:
        messages.info(request, "You should not have been there")
    return redirect("users:index")


def unsubscribe(request, slug):
    # print("unsubscribing")
    if request.method == "POST":
        try:
            bc = BookClub.objects.get(id=slug)
            if bc.admin == request.user:
                messages.info(
                    request,
                    "Owner can not unsubscribe, please reassign ownership first",
                )
                return redirect("users:index")
            if bc.polls != 0:
                poll = VotingPoll.objects.get(id=bc.polls)
                poll.remove_user_from_poll(request.user)
            bc.members.remove(request.user)
            messages.info(request, "Unsubscribe action complete")
        except ObjectDoesNotExist:
            print("Something went wrong")
    return redirect("users:index")


def register(request):
    if request.method == "POST":
        if "signup" in request.POST:
            form = UserRegisterForm(request.POST)
            request.session["register_form"] = request.POST
            if form.is_valid():
                vcode = "".join(random.choices(string.ascii_letters, k=5))
                email = form.cleaned_data.get("email")
                # print(f"vcode: {vcode}")
                request.session["verification_code"] = {
                    "code": vcode,
                    "ttl": (time.time() + 300),
                }
                subject, from_email, message = (
                    "Verify Your Email",
                    "test@gmail.com",
                    f"This is your verification code: {vcode}",
                )
                try:
                    send_mail(
                        subject,
                        message,
                        from_email,
                        [email],
                        fail_silently=False,
                    )
                    context = {
                        "form": form,
                        "title": "validate code",
                        "verify_code": True,
                    }
                    return render(request, "user/register.html", context)
                except SMTPException as e:
                    print(e)
                    context = {
                        "form": form,
                        "title": "validate code",
                        "verify_code": True,
                        "email_send_failed": True,
                    }
                    return render(request, "user/register.html", context)
        elif "verify" in request.POST:
            # print("Verify stuff")
            validate_form = ValidateForm(request.POST)
            # print(request.POST)
            if validate_form.is_valid():
                code = validate_form.cleaned_data.get("code")
                validation_token = request.session.get("verification_code")
                print(f"{validation_token}\n Time Now: {time.time()}")
                if validation_token and validation_token["ttl"] > time.time():
                    if code == validation_token["code"]:
                        post_req = request.session.pop("register_form")
                        form = UserRegisterForm(post_req)
                        form.save()
                        username = form.cleaned_data.get("username")
                        email = form.cleaned_data.get("email")
                        password = form.cleaned_data.get("password1")

                        user = authenticate(username=username, password=password)
                        login(request, user)
                        messages.success(
                            request,
                            "Your account has been created ! You are now able to log in",
                        )
                        del request.session["verification_code"]
                        return redirect("users:index")
                    else:
                        context = {
                            "title": "validate code",
                            "verify_code": True,
                            "validate_failed": True,
                            "error_text": "Incorrect Validation Code, \
make sure you entered in the right code.",
                        }
                        return render(request, "user/register.html", context)
                else:
                    context = {
                        "title": "validate code",
                        "verify_code": True,
                        "validate_failed": True,
                        "error_text": "The verification code has expired.",
                    }
                    return render(request, "user/register.html", context)
            else:
                print("Failed validation")

    else:
        form = UserRegisterForm()
    return render(
        request, "user/register.html", {"form": form, "title": "register here"}
    )


def user_login(request):
    if request.method == "POST":
        # TODO: use AuthenticationForm

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect("users:index")
        else:
            messages.info(request, "Account does not exist. Please sign up.")
    form = AuthenticationForm()
    return render(request, "user/login.html", {"form": form, "title": "log in"})


@login_required
def user_profile(request):
    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        # print("this one", request.POST)
        # if "change_password" in re
        if "update" in request.POST:
            if request.POST["email"] == request.user.email:
                # print("no email update")
                if user_form.is_valid():
                    user_form.save()
                    messages.success(request, "Your profile is updated successfully")
                    return redirect("users:user_profile")
                    # return render(request, "user/profile.html")
            # email changed
            request.session["profile_form"] = request.POST
            if request.POST["email"] != request.user.email:
                # print("email changed")
                if user_form.is_valid():
                    vcode = "".join(random.choices(string.ascii_letters, k=5))
                    email = user_form.cleaned_data.get("email")
                    # print(f"vcode: {vcode}")
                    request.session["verification_code"] = {
                        "code": vcode,
                        "ttl": (time.time() + 300),
                    }
                    subject, from_email, message = (
                        "Confirm your new email",
                        "test@gmail.com",
                        f"This is your verification code: {vcode}",
                    )
                    try:
                        send_mail(
                            subject,
                            message,
                            from_email,
                            [email],
                            fail_silently=False,
                        )
                        context = {
                            "form": user_form,
                            "title": "validate code",
                            "verify_code": True,
                        }
                        return render(request, "user/profile.html", context)
                    except SMTPException as e:
                        print(e)
                        context = {
                            "form": user_form,
                            "title": "validate code",
                            "verify_code": True,
                            "email_send_failed": True,
                        }
                        return render(request, "user/profile.html", context)
        elif "verify" in request.POST:
            validate_form = ValidateForm(request.POST)
            if validate_form.is_valid():
                code = validate_form.cleaned_data.get("code")
                validation_token = request.session.get("verification_code")
                print(f"{validation_token}\n Time Now: {time.time()}")
                if validation_token and validation_token["ttl"] > time.time():
                    if code == validation_token["code"]:
                        post_req = request.session.pop("profile_form")
                        user_form = UpdateUserForm(post_req, instance=request.user)
                        user_form.save()
                        messages.success(
                            request, "Your account has been updated successfully"
                        )
                        del request.session["verification_code"]
                        return redirect("users:user_profile")
                    else:
                        context = {
                            "title": "validate code",
                            "verify_code": True,
                            "validate_failed": True,
                            "error_text": "Incorrect Validation Code, \
make sure you entered in the right code.",
                        }
                        return render(request, "user/profile.html", context)
                else:
                    context = {
                        "title": "validate code",
                        "verify_code": True,
                        "validate_failed": True,
                        "error_text": "The verification code has expired.",
                    }
                    return render(request, "user/profile.html", context)
            else:
                context = {
                    "title": "validate code",
                    "verify_code": True,
                    "validate_failed": True,
                    "error_text": "Please enter a valid code!",
                }
                print("Failed validation")
                return render(request, "user/profile.html", context)
    else:
        user_form = UpdateUserForm(instance=request.user)
    return render(
        request,
        "user/profile.html",
        {"user_form": user_form, "title": "update your profile"},
    )


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = "user/change_password.html"
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy("users:index")


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "user/reset_password.html"
    email_template_name = "user/password_reset_email.html"
    subject_template_name = "user/password_reset_subject.txt"
    success_message = (
        "Instructions on how to reset your password were sent to you email. "
        "If you have an existing account with us, you should receive the email shortly. "
        "Make sure you have entered the correct email address and check your spam folder "
        "if you didn't receive an email."
    )
    success_url = reverse_lazy("users:password-reset")
