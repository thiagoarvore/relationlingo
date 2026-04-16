from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import FormView

from reports.models import DailyReport

from .forms import AnswerForm
from .models import Answer


class AnswerCreateView(FormView):
    form_class = AnswerForm
    template_name = "answers/respond.html"
    success_url = reverse_lazy("reports:about_me")

    same_day_message = "A resposta nao pode ser feita no mesmo dia do relatório."
    already_answered_message = "Este relatório ja possui resposta."

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

    def _get_report(self):
        return get_object_or_404(
            DailyReport.objects.select_related("reporter", "subject"),
            id=self.kwargs["report_id"],
            subject=self.request.user,
            active=True,
        )

    def _is_same_day(self, report):
        return timezone.localtime(report.created_at).date() == timezone.localdate()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self._get_report()
        context["report"] = report
        return context

    def get(self, request, *args, **kwargs):
        report = self._get_report()
        if self._is_same_day(report):
            messages.info(request, self.same_day_message)
            return redirect("reports:about_me")
        if Answer.objects.filter(report=report, active=True).exists():
            messages.info(request, self.already_answered_message)
            return redirect("reports:about_me")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        report = self._get_report()
        if self._is_same_day(report):
            messages.info(self.request, self.same_day_message)
            return redirect("reports:about_me")
        if Answer.objects.filter(report=report, active=True).exists():
            messages.info(self.request, self.already_answered_message)
            return redirect("reports:about_me")

        Answer.objects.create(
            report=report,
            text=form.cleaned_data["text"],
        )
        messages.success(self.request, "Resposta enviada com sucesso.")
        return super().form_valid(form)
