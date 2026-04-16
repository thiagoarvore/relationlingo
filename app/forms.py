from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django_base_kit.forms import SignUpForm
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string


class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": _("E-mail ou senha invalidos."),
        "inactive": _("Esta conta esta inativa."),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )
            if not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages["inactive"],
                    code="inactive",
                )
        return cleaned_data

    def get_user(self):
        return self.user_cache


class EmailOnlySignUpForm(SignUpForm):
    class Meta(SignUpForm.Meta):
        fields = [
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "username",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].label = "Nome"
        self.fields["first_name"].widget.attrs.update({"autocomplete": "given-name"})
        self.fields["last_name"].label = "Sobrenome"
        self.fields["last_name"].widget.attrs.update({"autocomplete": "family-name"})
        self.fields["username"].required = False
        self.fields["username"].widget = forms.HiddenInput()
        self.fields["username"].help_text = ""

    def _generate_unique_username(self):
        user_model = get_user_model()
        while True:
            candidate = f"user_{get_random_string(10).lower()}"
            if not user_model.objects.filter(username=candidate).exists():
                return candidate

    def save(self, commit=True):
        user = super().save(commit=False)
        username = (self.cleaned_data.get("username") or "").strip()
        user.username = username or self._generate_unique_username()
        if commit:
            user.save()
        return user
