from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from validate_email import validate_email
from .models import CustomUser


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "First Name", "class": "form-control"}
        ),
    )
    last_name = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Last Name", "class": "form-control"}
        ),
    )
    username = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        ),
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.TextInput(attrs={"placeholder": "email", "class": "form-control"}),
    )
    password1 = forms.CharField(
        max_length=20,
        required=True,
        label="Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        ),
    )
    password2 = forms.CharField(
        max_length=20,
        required=True,
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Re-enter Password", "class": "form-control"}
        ),
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        new = CustomUser.objects.filter(email=email)
        if new.count():
            raise forms.ValidationError(
                "Email already exists! Please use another email."
            )
        is_valid = validate_email(email)
        if not is_valid:
            raise forms.ValidationError("Incorrect email format!")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password.isnumeric():
            raise forms.ValidationError("Password cannot only contain numbers")
        elif password.isalpha():
            raise forms.ValidationError("Password cannot only contain characters")
        else:
            return password


class UpdateUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        try:
            self.fields["email"].initial = self.instance.email
        except CustomUser.DoesNotExist:
            pass

    username = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        ),
    )

    first_name = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "First Name", "class": "form-control"}
        ),
    )
    last_name = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Last Name", "class": "form-control"}
        ),
    )

    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.TextInput(attrs={"placeholder": "email", "class": "form-control"}),
    )

    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        new = CustomUser.objects.filter(email=email)
        if email != self.instance.email and new.count():
            raise forms.ValidationError(
                "Email already exists! Please use another email."
            )
        is_valid = validate_email(email)
        if not is_valid:
            raise forms.ValidationError("Incorrect email format!")
        return email


class ValidateForm(forms.Form):
    alphanumeric = RegexValidator(
        r"^[0-9a-zA-Z]*$", "Only alphanumeric characters are allowed."
    )
    code = forms.CharField(max_length=10, validators=[alphanumeric])

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if code.isalnum():
            return code
        raise forms.ValidationError("Code can only be alphanumeric")
