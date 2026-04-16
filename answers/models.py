from django.db import models
from django_base_kit.models import BaseModel
from reports.models import DailyReport


class Answer(BaseModel):
    report = models.OneToOneField(DailyReport, on_delete=models.CASCADE, related_name='answer')
    text = models.TextField()

    class Meta:
        verbose_name = 'Resposta'
        verbose_name_plural = 'Respostas'