from django.test import TestCase, Client
from django.urls import reverse

from .models import User


class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("board:login")
        self.email = "test@flatironschool.com"
        self.password = "password"
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_htmx_login_success(self):
        data = {"username": self.email, "password": self.password}
        headers = {"HX-Request": "true"}
        response = self.client.post(
            self.login_url, data=data, headers=headers, follow=False
        )

        self.assertIn("HX-Redirect", response.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_htmx_login_fail(self):
        data = {"username": self.email, "password": "wrong-password"}
        headers = {"HX-Request": "true"}
        response = self.client.post(
            self.login_url,
            data=data,
            headers=headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_already_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(self.login_url, follow=False)

        # Expecting a standard Django redirect
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class LogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse("board:logout")
        self.email = "test@flatironschool.com"
        self.password = "password"
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_user_logged_out(self):
        response = self.client.get(self.logout_url, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
