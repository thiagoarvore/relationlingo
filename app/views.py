import calendar

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db.models.functions import TruncDate
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import FormView
from django.views.generic import TemplateView

from pairs.models import Pair
from reports.models import DailyReport

from .forms import EmailLoginForm


class EmailLoginView(FormView):
    form_class = EmailLoginForm
    template_name = settings.BASE_KIT.get("login_template", "my_auth/login.html")
    success_url = settings.BASE_KIT.get("login_success_url", "/")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.POST.get("next") or self.request.GET.get("next")
        if redirect_to and url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return redirect_to
        return super().get_success_url()


class HomeView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy("login")
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        current_year = today.year
        current_month = today.month

        calendar.setfirstweekday(calendar.SUNDAY)
        month_weeks = calendar.monthcalendar(current_year, current_month)

        month_names_pt_br = [
            "",
            "Janeiro",
            "Fevereiro",
            "Marco",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
        ]

        partner_user = (
            Pair.objects.filter(Q(one=self.request.user) | Q(two=self.request.user), active=True)
            .select_related("one", "two")
            .first()
        )
        if partner_user:
            partner_user = (
                partner_user.two if partner_user.one_id == self.request.user.id else partner_user.one
            )

        current_tz = timezone.get_current_timezone()
        month_reports_qs = DailyReport.objects.filter(
            created_at__year=current_year,
            created_at__month=current_month,
            active=True,
        ).annotate(local_created_date=TruncDate("created_at", tzinfo=current_tz))

        user_report_days = {
            local_date.day
            for local_date in month_reports_qs.filter(reporter=self.request.user).values_list(
                "local_created_date", flat=True
            )
            if local_date
        }
        partner_report_days = set()
        if partner_user:
            partner_report_days = {
                local_date.day
                for local_date in month_reports_qs.filter(reporter=partner_user).values_list(
                    "local_created_date", flat=True
                )
                if local_date
            }

        calendar_weeks = []
        active_days = set()
        for week in month_weeks:
            row = []
            for day in week:
                if day == 0:
                    row.append({"day": 0, "tone": "empty", "date": ""})
                    continue

                tone = "default"
                if day in user_report_days:
                    tone = "mine"
                if day in partner_report_days:
                    tone = "partner"

                if tone in {"mine", "partner"}:
                    active_days.add(day)
                row.append(
                    {
                        "day": day,
                        "tone": tone,
                        "date": f"{current_year:04d}-{current_month:02d}-{day:02d}",
                    }
                )
            calendar_weeks.append(row)

        context["calendar_month_label"] = f"{month_names_pt_br[current_month]} {current_year}"
        context["calendar_weekdays"] = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"]
        context["calendar_weeks"] = calendar_weeks
        context["calendar_active_days"] = len(active_days)
        context["calendar_total_days"] = calendar.monthrange(current_year, current_month)[1]
        return context
