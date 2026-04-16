from django import forms

from .models import Answer


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text"]
        labels = {"text": "Sua resposta"}
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Escreva sua resposta para esse relatório.",
                }
            )
        }
