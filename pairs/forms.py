from django import forms


class PairInviteForm(forms.Form):
    email = forms.EmailField(
        label="E-mail da pessoa amada",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "amor@exemplo.com",
                "autocomplete": "email",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if self.request and self.request.user.is_authenticated:
            if email == self.request.user.email.strip().lower():
                raise forms.ValidationError("Voce nao pode enviar convite para seu proprio e-mail.")
        return email
