from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from crm.users.tests.factories import UserFactory


class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.data = {"username": "testuser", "password": "testpassword"}
        self.urls = {
            "token_obtain_pair": reverse("users:token_obtain_pair"),
            "token_refresh": reverse("users:token_refresh"),
            "token_verify": reverse("users:token_verify"),
            "token_blacklist": reverse("users:token_blacklist"),
            "user_me": reverse("api:user-me"),
        }
        self.refresh_invalid = {"refresh": "invalid"}

    def get_token(self) -> Response:
        response = self.client.post(self.urls.get("token_obtain_pair"), self.data, format="json")
        return response

    def test_obtain_token(self):
        UserFactory(**self.data)
        response = self.get_token()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_token_unknown(self):
        response = self.get_token()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        data = {"refresh": str(RefreshToken())}
        response = self.client.post(self.urls["token_refresh"], data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token_invalid(self):
        response = self.client.post(self.urls["token_refresh"], self.refresh_invalid, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_token(self):
        access_token = RefreshToken().access_token
        data = {"token": str(access_token)}
        response = self.client.post(self.urls["token_verify"], data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_token_invalid(self):
        response = self.client.post(self.urls["token_verify"], self.refresh_invalid, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        user = UserFactory(**self.data)
        self.client.force_login(user)
        response = self.get_token()
        data = {"refresh": response.data.get("refresh")}
        response = self.client.post(self.urls["token_blacklist"], data, format="json")
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_invalid(self):
        user = UserFactory(**self.data)
        self.client.force_login(user)
        response = self.get_token()
        data = {"refresh_token": "fsdf"}
        response = self.client.post(self.urls["token_blacklist"], data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data.get("validations"))

    def test_logout_anon(self):
        response = self.client.post(self.urls["token_blacklist"], self.refresh_invalid, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_protected_url(self):
        UserFactory(**self.data)
        # Access protected URL without token
        response = self.client.get(self.urls["user_me"])
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Get access token
        response = self.get_token()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data.get("access")
        # Set authorization header with bearer token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        # Access protected URL
        response = self.client.get(self.urls["user_me"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), self.data["username"])
