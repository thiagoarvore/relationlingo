from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, View

from pairs.models import Pair

from .forms import UserProfileForm


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:profile_edit")

    def _get_active_pair(self):
        return Pair.objects.filter(
            Q(one=self.request.user) | Q(two=self.request.user),
            active=True,
        ).first()

    def _get_partner_display(self, pair):
        if not pair:
            return "Sem parceria"

        partner = pair.two if pair.one_id == self.request.user.id else pair.one
        partner_name = (partner.first_name or "").strip()
        return partner_name or partner.email

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        pair = self._get_active_pair()
        kwargs["partner_display"] = self._get_partner_display(pair)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_active_pair"] = self._get_active_pair() is not None
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Perfil atualizado com sucesso.")
        return response


class PairUndoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pair = Pair.objects.filter(
            Q(one=request.user) | Q(two=request.user),
            active=True,
        ).first()
        if not pair:
            messages.info(request, "Voce nao possui parceria ativa para desfazer.")
            return redirect("accounts:profile_edit")

        pair.active = False
        pair.save(update_fields=["active", "updated_at"])
        messages.success(request, "Parceria desfeita com sucesso.")
        return redirect("accounts:profile_edit")
