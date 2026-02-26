from django.test import TestCase, Client
from django.urls import reverse

from .models import User


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
