from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from crm.users.tests.factories import SuperUserFactory

User = get_user_model()


class APITestCaseForChads(APITestCase):
    def setUp(self) -> None:
        # create django groups
        call_command("create_groups")
        # credentials
        self.credentials = {"password": "secretpass123"}

    def get_jwt_tokens(self, credentials: dict[str, str]):
        response = self.client.post(reverse("users:token_obtain_pair"), credentials, format="json")
        response = response.data.values()
        return response

    def authorize(self, user: User):
        if user is not None:
            # Authorize
            self.credentials.update({"username": user.username})
            _, access_token = self.get_jwt_tokens(self.credentials)
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def force_login(self) -> User:
        user = SuperUserFactory()
        self.client.force_login(user)
        return user

    def logout(self):
        self.client.credentials(HTTP_AUTHORIZATION="")

    def catch_error(self, response, expected_status):
        if response.status_code != expected_status:
            print(response.status_code, response.data)
            raise ValidationError(response.status_code, response.data)

    def get_request_factory(self, url: str, test_cases: list):
        for current_user, expected_status, *optional_args in test_cases:
            self.authorize(current_user)
            # Make request
            response = self.client.get(url)
            # Test response
            try:
                self.assertEqual(response.status_code, expected_status, *optional_args)
            except AssertionError:
                self.catch_error(response, expected_status)
            self.logout()

    def retrieve_request_factory(self, view_name: str, test_cases: list, lookup_arg: str = "pk"):
        for current_user, instance, expected_status, *optional_args in test_cases:
            self.authorize(current_user)
            # Make request
            url = reverse(view_name, args=[getattr(instance, lookup_arg)])
            response = self.client.get(url)
            # Test response
            try:
                self.assertEqual(response.status_code, expected_status, *optional_args)
            except AssertionError:
                self.catch_error(response, expected_status)
            self.logout()

    def post_request_factory(self, url: str, test_cases: list, multipart=False):
        request_fmt = "multipart" if multipart else "json"
        for current_user, payload, expected_status, *optional_args in test_cases:
            self.authorize(current_user)
            response = self.client.post(url, payload, format=request_fmt)
            # Test response
            try:
                self.assertEqual(response.status_code, expected_status, *optional_args)
            except AssertionError:
                self.catch_error(response, expected_status)
            self.logout()

    def put_request_factory(self, view_name: str, test_cases: list, lookup_arg: str = "pk", multipart=False):
        request_fmt = "multipart" if multipart else "json"
        for current_user, instance, payload, expected_status, *optional_args in test_cases:
            self.authorize(current_user)
            # Make request
            url = reverse(view_name, args=[getattr(instance, lookup_arg)])
            response = self.client.put(url, payload, format=request_fmt)
            # Test response
            try:
                self.assertEqual(response.status_code, expected_status, *optional_args)
            except AssertionError:
                self.catch_error(response, expected_status)
            self.logout()

    def delete_request_factory(self, view_name: str, test_cases: list, lookup_arg: str = "pk"):
        for current_user, instance, expected_status, *optional_args in test_cases:
            self.authorize(current_user)
            # Make request
            url = reverse(view_name, args=[getattr(instance, lookup_arg)])
            response = self.client.delete(url)
            # Test response
            try:
                self.assertEqual(response.status_code, expected_status, *optional_args)
            except AssertionError:
                self.catch_error(response, expected_status)
            self.logout()
