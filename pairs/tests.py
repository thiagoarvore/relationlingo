from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .forms import PairInviteForm
from .models import Pair, PairInvitation


class NavbarInviteButtonTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="navbar_user",
            email="navbar_user@example.com",
            password="SenhaForte123!",
        )

    def test_shows_invite_button_when_user_has_no_pair(self):
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertContains(response, "Convidar meu amor")

    def test_hides_invite_button_when_user_has_pair(self):
        user_model = get_user_model()
        partner = user_model.objects.create_user(
            username="navbar_partner",
            email="navbar_partner@example.com",
            password="SenhaForte123!",
        )
        Pair.objects.create(one=self.user, two=partner)

        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertNotContains(response, "Convidar meu amor")


class PairInviteViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="invite_user",
            email="invite_user@example.com",
            password="SenhaForte123!",
        )
        self.url = reverse("pairs:invite")

    def test_view_has_only_email_field(self):
        form = PairInviteForm()
        self.assertEqual(list(form.fields.keys()), ["email"])

    def test_logged_user_can_submit_invite_email_and_send_mail(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"email": "amor@example.com"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Convite enviado para amor@example.com.")

        invitation = PairInvitation.objects.get(inviter=self.user)
        self.assertEqual(invitation.invited_email, "amor@example.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(str(invitation.token), mail.outbox[0].body)

    def test_invite_page_contains_htmx_attributes(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, 'hx-post="/pairs/convidar/"')
        self.assertContains(response, 'hx-target="#invite-form-shell"')

    def test_htmx_post_updates_only_form_block(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {"email": "amor@example.com"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="invite-form-shell"')
        self.assertContains(response, "Convite enviado para amor@example.com.")


class PairInvitationAcceptTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.inviter = user_model.objects.create_user(
            username="inviter",
            email="inviter@example.com",
            password="SenhaForte123!",
        )
        self.invite_url = reverse("pairs:invite")

    def _create_invitation(self, email):
        self.client.force_login(self.inviter)
        self.client.post(self.invite_url, {"email": email})
        return PairInvitation.objects.get(inviter=self.inviter, invited_email=email)

    def test_existing_user_accept_creates_pair(self):
        user_model = get_user_model()
        invited = user_model.objects.create_user(
            username="invited_existing",
            email="invited_existing@example.com",
            password="SenhaForte123!",
        )
        invitation = self._create_invitation(invited.email)

        self.client.force_login(invited)
        response = self.client.get(
            reverse("pairs:invite_accept", kwargs={"token": invitation.token}),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Pair.objects.filter(one=self.inviter, two=invited).exists()
            or Pair.objects.filter(one=invited, two=self.inviter).exists()
        )
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_accepted)
        self.assertEqual(invitation.invitee, invited)

    def test_existing_user_without_session_logs_in_and_accepts_with_next(self):
        user_model = get_user_model()
        invited = user_model.objects.create_user(
            username="invited_login_flow",
            email="invited_login_flow@example.com",
            password="SenhaForte123!",
        )
        invitation = self._create_invitation(invited.email)
        self.client.logout()

        accept_url = reverse("pairs:invite_accept", kwargs={"token": invitation.token})
        response = self.client.get(accept_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/?next=", response.url)

        login_response = self.client.post(
            reverse("login"),
            {
                "email": invited.email,
                "password": "SenhaForte123!",
                "next": accept_url,
            },
            follow=True,
        )
        self.assertEqual(login_response.status_code, 200)

        self.assertTrue(
            Pair.objects.filter(one=self.inviter, two=invited).exists()
            or Pair.objects.filter(one=invited, two=self.inviter).exists()
        )
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_accepted)

    def test_new_user_flow_redirects_to_signup_and_creates_pair_after_signup(self):
        invited_email = "new_invited@example.com"
        invitation = self._create_invitation(invited_email)
        self.client.logout()

        accept_url = reverse("pairs:invite_accept", kwargs={"token": invitation.token})
        response = self.client.get(accept_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/signup/?invite_token=", response.url)

        signup_url = f"{reverse('signup')}?invite_token={invitation.token}"
        response = self.client.post(
            signup_url,
            {
                "email": invited_email,
                "password1": "SenhaForte123!",
                "password2": "SenhaForte123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        user_model = get_user_model()
        invited_user = user_model.objects.get(email=invited_email)
        self.assertTrue(
            Pair.objects.filter(one=self.inviter, two=invited_user).exists()
            or Pair.objects.filter(one=invited_user, two=self.inviter).exists()
        )
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_accepted)
        self.assertEqual(invitation.invitee, invited_user)
