from django.contrib import messages
from django.db.models import Q
from django.db.models import Exists, OuterRef
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView

from answers.models import Answer
from pairs.models import Pair

from .forms import DailyReportForm
from .models import DailyReport


class DailyReportCreateView(FormView):
    form_class = DailyReportForm
    template_name = "reports/create.html"
    partial_template_name = "reports/partials/daily_report_form.html"
    success_url = reverse_lazy("reports:create")
    no_pair_message = "Voce precisa ter um par para criar um relatório diario."
    report_already_filled_message = "Relatório de hoje já preenchido"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

    def _is_htmx_request(self):
        return self.request.headers.get("HX-Request") == "true"

    def _get_active_pair(self):
        return Pair.objects.filter(
            Q(one=self.request.user) | Q(two=self.request.user),
            active=True,
        ).first()

    def _get_subject(self, pair):
        if pair.one_id == self.request.user.id:
            return pair.two
        return pair.one

    def _has_report_today(self):
        current_tz = timezone.get_current_timezone()
        return (
            DailyReport.objects.filter(
                reporter=self.request.user,
                active=True,
            )
            .annotate(local_created_date=TruncDate("created_at", tzinfo=current_tz))
            .filter(local_created_date=timezone.localdate())
            .exists()
        )

    def _render_no_pair_response(self):
        if self._is_htmx_request():
            return render(
                self.request,
                self.partial_template_name,
                {
                    "form": self.form_class(),
                    "no_pair_message": self.no_pair_message,
                    "has_pair": False,
                },
                status=403,
            )

        messages.error(self.request, self.no_pair_message)
        return redirect("reports:create")

    def _render_report_already_filled_response(self):
        if self._is_htmx_request():
            return render(
                self.request,
                self.partial_template_name,
                {
                    "form": self.form_class(),
                    "has_pair": True,
                    "has_report_today": True,
                    "today_report_message": self.report_already_filled_message,
                },
                status=403,
            )

        messages.info(self.request, self.report_already_filled_message)
        return redirect("reports:create")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pair = self._get_active_pair()
        subject = self._get_subject(pair) if pair else None
        has_report_today = self._has_report_today() if pair else False
        context["has_pair"] = pair is not None
        context["pair_user"] = subject
        context["has_report_today"] = has_report_today
        context["today_report_message"] = self.report_already_filled_message
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self._get_active_pair():
            return self._render_no_pair_response()
        if self._has_report_today():
            return self._render_report_already_filled_response()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        pair = self._get_active_pair()
        if not pair:
            return self._render_no_pair_response()
        if self._has_report_today():
            return self._render_report_already_filled_response()

        subject = self._get_subject(pair)
        DailyReport.objects.create(
            reporter=self.request.user,
            subject=subject,
            critic=form.cleaned_data["critic"],
            critic_level=form.cleaned_data["critic_level"],
            compliment=form.cleaned_data["compliment"],
        )
        success_message = "Relatório diario criado com sucesso."

        if self._is_htmx_request():
            return render(
                self.request,
                self.partial_template_name,
                {
                    "form": self.form_class(),
                    "inline_success_message": success_message,
                    "has_pair": True,
                    "has_report_today": True,
                    "today_report_message": self.report_already_filled_message,
                },
            )

        messages.success(self.request, success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        if self._is_htmx_request():
            return render(
                self.request,
                self.partial_template_name,
                {
                    "form": form,
                    "has_pair": True,
                },
                status=422,
            )
        return super().form_invalid(form)


class DailyReportListView(ListView):
    model = DailyReport
    template_name = "reports/list.html"
    context_object_name = "reports"
    paginate_by = 31

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = DailyReport.objects.filter(reporter=self.request.user).select_related(
            "subject"
        )
        filter_date = self.request.GET.get("date", "").strip()
        if filter_date:
            current_tz = timezone.get_current_timezone()
            queryset = queryset.annotate(
                local_created_date=TruncDate("created_at", tzinfo=current_tz)
            ).filter(local_created_date=filter_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_date"] = self.request.GET.get("date", "").strip()
        return context


class DailyReportAboutMeListView(ListView):
    model = DailyReport
    template_name = "reports/about_me.html"
    context_object_name = "reports"
    paginate_by = 31

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = (
            DailyReport.objects.filter(subject=self.request.user)
            .select_related("reporter")
            .annotate(
                has_answer=Exists(
                    Answer.objects.filter(
                        report_id=OuterRef("pk"),
                        active=True,
                    )
                )
            )
        )
        filter_date = self.request.GET.get("date", "").strip()
        if filter_date:
            current_tz = timezone.get_current_timezone()
            queryset = queryset.annotate(
                local_created_date=TruncDate("created_at", tzinfo=current_tz)
            ).filter(local_created_date=filter_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_date"] = self.request.GET.get("date", "").strip()
        today = timezone.localdate()
        for report in context["reports"]:
            report_is_today = timezone.localtime(report.created_at).date() == today
            report.is_from_today = report_is_today
            report.can_answer = (not report_is_today) and (not report.has_answer)
        return context


class DailyReportDetailView(DetailView):
    model = DailyReport
    template_name = "reports/detail.html"
    context_object_name = "report"
    pk_url_kwarg = "report_id"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        base_qs = DailyReport.objects.select_related("reporter", "subject")
        return get_object_or_404(
            base_qs.filter(
                Q(reporter=self.request.user) | Q(subject=self.request.user),
                active=True,
            ),
            pk=self.kwargs["report_id"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = context["report"]
        try:
            context["answer"] = report.answer if report.answer.active else None
        except Answer.DoesNotExist:
            context["answer"] = None
        return context
