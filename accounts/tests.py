from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from pairs.models import Pair


class UserProfileUpdateViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="perfil_teste",
            email="perfil_teste@example.com",
            password="SenhaForte123!",
            first_name="Nome",
            last_name="Antigo",
        )
        self.url = reverse("accounts:profile_edit")

    def test_redirects_anonymous_user_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_updates_logged_user_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {
                "first_name": "Novo",
                "last_name": "Sobrenome",
                "email": "novo@example.com",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Novo")
        self.assertEqual(self.user.last_name, "Sobrenome")
        self.assertEqual(self.user.email, "novo@example.com")

    def test_navbar_has_profile_button_for_logged_user(self):
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("accounts:profile_edit"))
        self.assertContains(response, "Perfil")

    def test_profile_shows_partnership_field_without_pair(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Parceria atual")
        self.assertContains(response, "Sem parceria")

    def test_profile_shows_partner_and_can_undo_pair(self):
        user_model = get_user_model()
        partner = user_model.objects.create_user(
            username="partner_teste",
            email="partner_teste@example.com",
            password="SenhaForte123!",
            first_name="Amor",
        )
        pair = Pair.objects.create(one=self.user, two=partner)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, "Amor")
        self.assertContains(response, "Desfazer parceria")

        undo_url = reverse("accounts:pair_undo")
        response = self.client.post(undo_url, follow=True)
        self.assertEqual(response.status_code, 200)
        pair.refresh_from_db()
        self.assertFalse(pair.active)
