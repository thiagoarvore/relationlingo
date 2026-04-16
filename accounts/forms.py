from django import forms
from django.contrib.auth import get_user_model


class UserProfileForm(forms.ModelForm):
    partnership = forms.CharField(
        label="Parceria atual",
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    def __init__(self, *args, **kwargs):
        partner_display = kwargs.pop("partner_display", "Sem parceria")
        super().__init__(*args, **kwargs)
        self.fields["partnership"].initial = partner_display
        self.order_fields(["first_name", "last_name", "email", "partnership"])

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = self._meta.model.objects.filter(email__iexact=email).exclude(
            pk=self.instance.pk
        )
        if qs.exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email
