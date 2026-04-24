from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, View

from app.forms import EmailOnlySignUpForm

from .forms import PairInviteForm
from .models import PairInvitation
from .services import create_pair_between_users


class PairInviteView(FormView):
    form_class = PairInviteForm
    template_name = "pairs/invite.html"
    partial_template_name = "pairs/partials/invite_form.html"
    success_url = reverse_lazy("pairs:invite")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

    def _is_htmx_request(self):
        return self.request.headers.get("HX-Request") == "true"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def _send_invitation_email(self, invitation):
        accept_url = self.request.build_absolute_uri(
            reverse("pairs:invite_accept", kwargs={"token": invitation.token})
        )
        inviter_name = self.request.user.first_name or self.request.user.username
        invited_user_exists = (
            get_user_model()
            .objects.filter(email__iexact=invitation.invited_email)
            .exists()
        )
        html_template_name = (
            "email_templates/pair_invite_existing_profile.html"
            if invited_user_exists
            else "email_templates/pair_invite_new_profile.html"
        )
        subject = "Convite no RelationLingo"
        message = (
            f"{inviter_name} te convidou para formar um par no RelationLingo.\n\n"
            f"Para aceitar, acesse:\n{accept_url}\n\n"
            "Se voce nao esperava esse convite, ignore este e-mail."
        )
        html_message = render_to_string(
            html_template_name,
            {
                "inviter_name": inviter_name,
                "accept_url": accept_url,
            },
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.invited_email],
            html_message=html_message,
            fail_silently=False,
        )

    def form_valid(self, form):
        invited_email = form.cleaned_data["email"]
        invitation = PairInvitation.objects.create(
            inviter=self.request.user,
            invited_email=invited_email,
        )
        self._send_invitation_email(invitation)
        success_message = f"Convite enviado para {invited_email}."

        if self._is_htmx_request():
            return render(
                self.request,
                self.partial_template_name,
                {
                    "form": self.form_class(request=self.request),
                    "inline_success_message": success_message,
                },
            )

        messages.success(self.request, success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        if self._is_htmx_request():
            return render(
                self.request,
                self.partial_template_name,
                {"form": form},
                status=422,
            )
        return super().form_invalid(form)


class PairInvitationAcceptView(View):
    def get(self, request, token):
        invitation = get_object_or_404(PairInvitation, token=token)

        if invitation.is_accepted:
            messages.info(request, "Este convite ja foi aceito anteriormente.")
            return redirect("home")

        invited_email = invitation.invited_email.strip().lower()
        user_model = get_user_model()
        invited_user_exists = user_model.objects.filter(
            email__iexact=invited_email
        ).exists()

        if not request.user.is_authenticated:
            if invited_user_exists:
                messages.info(
                    request, "Entre com o e-mail convidado para aceitar o convite."
                )
                login_url = reverse("login")
                query = urlencode({"next": request.path})
                return redirect(f"{login_url}?{query}")

            signup_url = reverse("signup")
            query = urlencode({"invite_token": str(invitation.token)})
            messages.info(request, "Crie sua conta para concluir o aceite do convite.")
            return redirect(f"{signup_url}?{query}")

        user_email = (request.user.email or "").strip().lower()
        if user_email != invited_email:
            messages.error(
                request,
                f"Este convite foi enviado para {invited_email}. Entre com esse e-mail para aceitar.",
            )
            return redirect("home")

        try:
            pair, _ = create_pair_between_users(invitation.inviter, request.user)
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("home")

        invitation.mark_as_accepted(request.user, pair)
        messages.success(request, "Convite aceito com sucesso. O par foi criado.")
        return redirect("home")


class InvitationSignUpView(FormView):
    form_class = EmailOnlySignUpForm
    template_name = "my_auth/signup.html"
    success_url = reverse_lazy("home")

    def get_initial(self):
        initial = super().get_initial()
        invite_token = self.request.GET.get("invite_token")
        if not invite_token:
            return initial

        invitation = PairInvitation.objects.filter(
            token=invite_token, accepted_at__isnull=True
        ).first()
        if invitation:
            initial["email"] = invitation.invited_email
        return initial

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invite_token = self.request.GET.get("invite_token", "")
        context["invite_token"] = invite_token
        invitation = None
        if invite_token:
            invitation = PairInvitation.objects.filter(
                token=invite_token, accepted_at__isnull=True
            ).first()
        context["invitation"] = invitation
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)

        invite_token = self.request.GET.get("invite_token")
        if not invite_token:
            messages.success(self.request, "Conta criada com sucesso.")
            return super().form_valid(form)

        invitation = PairInvitation.objects.filter(
            token=invite_token, accepted_at__isnull=True
        ).first()
        if not invitation:
            messages.info(
                self.request,
                "Conta criada, mas o convite nao foi encontrado ou ja foi usado.",
            )
            return super().form_valid(form)

        if user.email.strip().lower() != invitation.invited_email.strip().lower():
            messages.error(
                self.request,
                "Conta criada, mas o e-mail nao corresponde ao e-mail convidado.",
            )
            return super().form_valid(form)

        try:
            pair, _ = create_pair_between_users(invitation.inviter, user)
        except ValueError as exc:
            messages.error(self.request, str(exc))
            return super().form_valid(form)

        invitation.mark_as_accepted(user, pair)
        messages.success(self.request, "Conta criada e convite aceito com sucesso.")
        return super().form_valid(form)
