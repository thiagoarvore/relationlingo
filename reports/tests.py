from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from answers.models import Answer
from pairs.models import Pair

from .models import DailyReport


class DailyReportCreateViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="reporter_user",
            email="reporter@example.com",
            password="SenhaForte123!",
        )
        self.partner = user_model.objects.create_user(
            username="partner_user",
            email="partner@example.com",
            password="SenhaForte123!",
        )
        self.create_url = reverse("reports:create")

    def _payload(self):
        return {
            "critic": "Poderiamos conversar melhor no fim do dia.",
            "critic_level": "red",
            "compliment": "Voce foi muito parceira hoje.",
        }

    def _create_today_report(self):
        return DailyReport.objects.create(
            reporter=self.user,
            subject=self.partner,
            critic="Ja preenchido hoje.",
            critic_level=2,
            compliment="Elogio do dia.",
        )

    def test_get_without_pair_hides_form_in_front(self):
        self.client.force_login(self.user)
        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Voce precisa ter um par para criar um relatório diario.")
        self.assertNotContains(response, "<form")

    def test_post_without_pair_is_blocked_in_back(self):
        self.client.force_login(self.user)
        response = self.client.post(self.create_url, self._payload(), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(DailyReport.objects.count(), 0)
        self.assertContains(response, "Voce precisa ter um par para criar um relatório diario.")

    def test_htmx_post_without_pair_is_blocked(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.create_url,
            self._payload(),
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(DailyReport.objects.count(), 0)
        self.assertContains(response, 'id="daily-report-form-shell"', status_code=403)
        self.assertContains(
            response,
            "Voce precisa ter um par para criar um relatório diario.",
            status_code=403,
        )

    def test_post_with_pair_creates_report_with_fixed_reporter_and_subject(self):
        Pair.objects.create(one=self.user, two=self.partner)
        self.client.force_login(self.user)

        response = self.client.post(self.create_url, self._payload(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(DailyReport.objects.count(), 1)

        report = DailyReport.objects.get()
        self.assertEqual(report.reporter, self.user)
        self.assertEqual(report.subject, self.partner)
        self.assertEqual(report.critic_level, 3)
        self.assertContains(response, "Relatório diario criado com sucesso.")

    def test_htmx_post_with_pair_updates_form_shell(self):
        Pair.objects.create(one=self.user, two=self.partner)
        self.client.force_login(self.user)

        response = self.client.post(
            self.create_url,
            self._payload(),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(DailyReport.objects.count(), 1)
        self.assertContains(response, 'id="daily-report-form-shell"')
        self.assertContains(response, "Relatório diario criado com sucesso.")

    def test_form_partial_has_htmx_attributes(self):
        Pair.objects.create(one=self.user, two=self.partner)
        self.client.force_login(self.user)

        response = self.client.get(self.create_url)
        self.assertContains(response, 'hx-post="/reports/novo/"')
        self.assertContains(response, 'hx-target="#daily-report-form-shell"')

    def test_get_with_today_report_shows_message_and_hides_form(self):
        Pair.objects.create(one=self.user, two=self.partner)
        self._create_today_report()
        self.client.force_login(self.user)

        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Relatório de hoje já preenchido")
        self.assertNotContains(response, "<form")

    def test_post_with_today_report_is_blocked(self):
        Pair.objects.create(one=self.user, two=self.partner)
        self._create_today_report()
        self.client.force_login(self.user)

        response = self.client.post(self.create_url, self._payload(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(DailyReport.objects.count(), 1)
        self.assertContains(response, "Relatório de hoje já preenchido")

    def test_htmx_post_with_today_report_is_blocked(self):
        Pair.objects.create(one=self.user, two=self.partner)
        self._create_today_report()
        self.client.force_login(self.user)

        response = self.client.post(
            self.create_url,
            self._payload(),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(DailyReport.objects.count(), 1)
        self.assertContains(response, "Relatório de hoje já preenchido", status_code=403)

    def test_navbar_hides_report_button_when_today_report_exists(self):
        Pair.objects.create(one=self.user, two=self.partner)
        self._create_today_report()
        self.client.force_login(self.user)

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Relatório diario")

    def test_yesterday_report_does_not_block_today_creation(self):
        Pair.objects.create(one=self.user, two=self.partner)
        yesterday_report = self._create_today_report()
        DailyReport.objects.filter(pk=yesterday_report.pk).update(
            created_at=timezone.now() - timezone.timedelta(days=1)
        )
        self.client.force_login(self.user)

        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Relatório de hoje já preenchido")
        self.assertContains(response, "<form")


class DailyReportListViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="reports_owner",
            email="owner@example.com",
            password="SenhaForte123!",
        )
        self.partner = user_model.objects.create_user(
            username="reports_partner",
            email="partner2@example.com",
            password="SenhaForte123!",
        )
        self.other_user = user_model.objects.create_user(
            username="reports_other",
            email="other@example.com",
            password="SenhaForte123!",
        )
        self.list_url = reverse("reports:list")
        self.about_me_url = reverse("reports:about_me")

    def test_list_shows_only_reports_created_by_logged_user(self):
        own_report = DailyReport.objects.create(
            reporter=self.user,
            subject=self.partner,
            critic="Critica 1",
            critic_level=2,
            compliment="Elogio 1",
        )
        other_report = DailyReport.objects.create(
            reporter=self.other_user,
            subject=self.partner,
            critic="Critica 2",
            critic_level=3,
            compliment="Elogio 2",
        )

        self.client.force_login(self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, reverse("reports:detail", kwargs={"report_id": own_report.id})
        )
        self.assertNotContains(
            response, reverse("reports:detail", kwargs={"report_id": other_report.id})
        )

    def test_list_filter_by_date(self):
        today_report = DailyReport.objects.create(
            reporter=self.user,
            subject=self.partner,
            critic="Critica de hoje",
            critic_level=1,
            compliment="Elogio de hoje",
        )
        yesterday_report = DailyReport.objects.create(
            reporter=self.user,
            subject=self.partner,
            critic="Critica de ontem",
            critic_level=2,
            compliment="Elogio de ontem",
        )
        DailyReport.objects.filter(pk=yesterday_report.pk).update(
            created_at=timezone.now() - timezone.timedelta(days=1)
        )
        today_str = timezone.localdate().isoformat()

        self.client.force_login(self.user)
        response = self.client.get(f"{self.list_url}?date={today_str}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, reverse("reports:detail", kwargs={"report_id": today_report.id})
        )
        self.assertNotContains(
            response, reverse("reports:detail", kwargs={"report_id": yesterday_report.id})
        )
        self.assertContains(response, f'value="{today_str}"')

    def test_about_me_list_shows_only_reports_where_logged_user_is_subject(self):
        about_me_report = DailyReport.objects.create(
            reporter=self.partner,
            subject=self.user,
            critic="Critica sobre mim",
            critic_level=1,
            compliment="Elogio sobre mim",
        )
        DailyReport.objects.create(
            reporter=self.user,
            subject=self.partner,
            critic="Critica que eu fiz",
            critic_level=2,
            compliment="Elogio que eu fiz",
        )

        self.client.force_login(self.user)
        response = self.client.get(self.about_me_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, reverse("reports:detail", kwargs={"report_id": about_me_report.id})
        )
        self.assertNotContains(response, "Responder")

        DailyReport.objects.filter(pk=about_me_report.pk).update(
            created_at=timezone.now() - timezone.timedelta(days=1)
        )
        response = self.client.get(self.about_me_url)
        self.assertContains(response, "Responder")

        Answer.objects.create(report=about_me_report, text="Minha resposta")
        response = self.client.get(self.about_me_url)
        self.assertContains(response, "Respondido")

    def test_about_me_list_filter_by_date(self):
        report_today = DailyReport.objects.create(
            reporter=self.partner,
            subject=self.user,
            critic="Critica hoje sobre mim",
            critic_level=1,
            compliment="Elogio hoje sobre mim",
        )
        report_yesterday = DailyReport.objects.create(
            reporter=self.partner,
            subject=self.user,
            critic="Critica ontem sobre mim",
            critic_level=2,
            compliment="Elogio ontem sobre mim",
        )
        DailyReport.objects.filter(pk=report_yesterday.pk).update(
            created_at=timezone.now() - timezone.timedelta(days=1)
        )
        today_str = timezone.localdate().isoformat()

        self.client.force_login(self.user)
        response = self.client.get(f"{self.about_me_url}?date={today_str}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, reverse("reports:detail", kwargs={"report_id": report_today.id})
        )
        self.assertNotContains(
            response, reverse("reports:detail", kwargs={"report_id": report_yesterday.id})
        )
        self.assertContains(response, f'value="{today_str}"')

    def test_report_detail_shows_answer_when_exists(self):
        report = DailyReport.objects.create(
            reporter=self.user,
            subject=self.partner,
            critic="Critica detalhada",
            critic_level=3,
            compliment="Elogio detalhado",
        )
        Answer.objects.create(report=report, text="Resposta detalhada")

        self.client.force_login(self.user)
        detail_url = reverse("reports:detail", kwargs={"report_id": report.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Critica detalhada")
        self.assertContains(response, "Resposta detalhada")

    def test_report_detail_denies_user_outside_report(self):
        outsider = get_user_model().objects.create_user(
            username="outsider_user",
            email="outsider@example.com",
            password="SenhaForte123!",
        )
        report = DailyReport.objects.create(
            reporter=self.user,
            subject=self.partner,
            critic="Critica privada",
            critic_level=2,
            compliment="Elogio privado",
        )
        self.client.force_login(outsider)
        detail_url = reverse("reports:detail", kwargs={"report_id": report.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)
