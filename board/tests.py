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


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile_url = reverse("board:profile")
        self.email = "test@flatironschool.com"
        self.password = "password"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            first_name="Test",
            last_name="User",
        )

    def test_profile_requires_login(self):
        response = self.client.get(self.profile_url, follow=False)

        self.assertEqual(response.status_code, 302)

    def test_profile_page_loads_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.email)
        self.assertContains(response, "Test")
        self.assertContains(response, "User")

    def test_profile_form_is_prepopulated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)

        self.assertContains(response, 'value="test@flatironschool.com"', html=False)
        self.assertContains(response, 'value="Test"', html=False)
        self.assertContains(response, 'value="User"', html=False)

    def test_htmx_profile_update_success(self):
        self.client.force_login(self.user)
        data = {
            "email": "updated@flatironschool.com",
            "first_name": "Updated",
            "last_name": "Name",
        }
        headers = {"HX-Request": "true"}

        response = self.client.post(
            self.profile_url,
            data=data,
            headers=headers,
            follow=False,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Profile updated successfully.")

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updated@flatironschool.com")
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")

    def test_htmx_profile_update_requires_email(self):
        self.client.force_login(self.user)
        data = {
            "email": "",
            "first_name": "Updated",
            "last_name": "Name",
        }
        headers = {"HX-Request": "true"}

        response = self.client.post(
            self.profile_url,
            data=data,
            headers=headers,
            follow=False,
        )

        self.assertEqual(response.status_code, 422)
        self.assertContains(response, "This field is required.", status_code=422)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.last_name, "User")
