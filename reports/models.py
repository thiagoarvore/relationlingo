from django.conf import settings
from django.db import models
from django_base_kit.models import BaseModel

# Create your models here.
user_model = settings.AUTH_USER_MODEL


class DailyReport(BaseModel):
    reporter = models.ForeignKey(
        user_model, on_delete=models.CASCADE, related_name="reports_as_reporter"
    )
    subject = models.ForeignKey(
        user_model, on_delete=models.CASCADE, related_name="reports_as_subject"
    )
    critic = models.TextField()
    critic_level = models.PositiveSmallIntegerField(default=1)
    compliment = models.TextField()

    def __str__(self):
        date = self.created_at.strftime("%d/%m/%y")
        return f"{date} - {self.critic_level}"

    class Meta:
        verbose_name = "Relatório diário"
        verbose_name_plural = "Relatórios diários"
        ordering = ["-created_at"]
        default_permissions = ("add", "view")
