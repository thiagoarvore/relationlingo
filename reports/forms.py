from django import forms

from .models import DailyReport


class DailyReportForm(forms.ModelForm):
    COLOR_LEVEL_CHOICES = (
        ("green", "Verde"),
        ("yellow", "Amarelo"),
        ("red", "Vermelho"),
    )
    COLOR_TO_LEVEL = {"green": 1, "yellow": 2, "red": 3}

    critic_level = forms.ChoiceField(
        choices=COLOR_LEVEL_CHOICES,
        label="Nivel da critica",
    )

    class Meta:
        model = DailyReport
        fields = ["critic", "critic_level", "compliment"]
        labels = {
            "critic": "Critica",
            "critic_level": "Nivel da critica",
            "compliment": "Elogio",
        }
        widgets = {
            "critic": forms.Textarea(attrs={"rows": 4}),
            "compliment": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_critic_level(self):
        color_level = self.cleaned_data["critic_level"]
        mapped_level = self.COLOR_TO_LEVEL.get(color_level)
        if mapped_level is None:
            raise forms.ValidationError("Selecione um nivel de critica valido.")
        return mapped_level
