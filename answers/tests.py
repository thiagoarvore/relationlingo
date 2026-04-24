from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from reports.models import DailyReport

from .models import Answer


class AnswerCreateViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.subject_user = user_model.objects.create_user(
            username="subject_user",
            email="subject@example.com",
            password="SenhaForte123!",
        )
        self.reporter_user = user_model.objects.create_user(
            username="reporter_user_answer",
            email="reporter@example.com",
            password="SenhaForte123!",
        )
        self.other_user = user_model.objects.create_user(
            username="other_user_answer",
            email="other@example.com",
            password="SenhaForte123!",
        )

    def _create_report_about_subject(self):
        return DailyReport.objects.create(
            reporter=self.reporter_user,
            subject=self.subject_user,
            critic="Critica do report",
            critic_level=2,
            compliment="Elogio do report",
        )

    def test_subject_can_answer_after_report_day(self):
        report = self._create_report_about_subject()
        DailyReport.objects.filter(pk=report.pk).update(
            created_at=timezone.now() - timezone.timedelta(days=1)
        )
        self.client.force_login(self.subject_user)
        url = reverse("answers:create", kwargs={"report_id": report.id})

        response = self.client.post(url, {"text": "Minha resposta"}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Answer.objects.count(), 1)
        answer = Answer.objects.get()
        self.assertEqual(answer.report_id, report.id)
        self.assertEqual(answer.text, "Minha resposta")
        self.assertContains(response, "Resposta enviada com sucesso.")

    def test_same_day_answer_is_blocked(self):
        report = self._create_report_about_subject()
        self.client.force_login(self.subject_user)
        url = reverse("answers:create", kwargs={"report_id": report.id})

        response = self.client.post(
            url, {"text": "Tentativa no mesmo dia"}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Answer.objects.count(), 0)
        self.assertContains(
            response, "A resposta nao pode ser feita no mesmo dia do relatório."
        )

    def test_non_subject_cannot_answer(self):
        report = self._create_report_about_subject()
        DailyReport.objects.filter(pk=report.pk).update(
            created_at=timezone.now() - timezone.timedelta(days=1)
        )
        self.client.force_login(self.other_user)
        url = reverse("answers:create", kwargs={"report_id": report.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_answer_twice(self):
        report = self._create_report_about_subject()
        DailyReport.objects.filter(pk=report.pk).update(
            created_at=timezone.now() - timezone.timedelta(days=1)
        )
        Answer.objects.create(report=report, text="Primeira resposta")
        self.client.force_login(self.subject_user)
        url = reverse("answers:create", kwargs={"report_id": report.id})

        response = self.client.post(url, {"text": "Segunda resposta"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Answer.objects.count(), 1)
        self.assertContains(response, "Este relatório ja possui resposta.")
