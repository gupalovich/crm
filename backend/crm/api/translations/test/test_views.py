from django.urls import reverse
from faker import Faker
from rest_framework import status

from crm.api.utils import APITestCaseForChads
from crm.companies.tests.factories import (
    CompanyFactory,
    CompanyMemberFactory,
    ProductTranslation,
    ProductTranslationFactory,
)
from crm.users.tests.factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory


class ProductTranslationViewsetTests(APITestCaseForChads):
    def setUp(self):
        super().setUp()
        # test data
        self.fake = Faker()
        self.credentials = {"password": "secretpass123"}
        # create users
        self.superuser = SuperUserFactory(**self.credentials)
        self.admin = AdminUserFactory(**self.credentials)
        self.manager = ManagerUserFactory(**self.credentials)
        self.other_superuser = SuperUserFactory(**self.credentials)
        # create translations
        self.translation = ProductTranslationFactory()
        self.other_translation = ProductTranslationFactory()
        # create companies
        self.company = CompanyFactory()
        self.other_company = CompanyFactory()
        # Create company memberships
        self.member_superuser = CompanyMemberFactory(user=self.superuser, company=self.company)
        self.member_admin = CompanyMemberFactory(user=self.admin, company=self.company)
        self.member_manager = CompanyMemberFactory(user=self.manager, company=self.company)
        self.member_other = CompanyMemberFactory(user=self.other_superuser, company=self.other_company)
        # urls
        self.urls = {
            "list": reverse("api:translation-list"),
            "detail": reverse("api:translation-detail", args=[self.translation.id]),
            "detail_raw": "api:translation-detail",
            "add": reverse("api:translation-add"),
            "ids": reverse("api:translation-ids"),
        }
        # list test cases
        self.list_cases = [  # (current_user, response_status, info_msg)
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see translation list"),
            (self.admin, status.HTTP_403_FORBIDDEN, "ADMIN can't see translation list"),
            (self.manager, status.HTTP_403_FORBIDDEN, "MANAGER can't see translation list"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see translation list"),
        ]
        # create test cases
        self.create_cases = [  # (current_user, to_create, response_status, info_msg)
            (
                self.superuser,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "SUPERUSER can create translation",
            ),
            (
                self.admin,
                self.build_post_data(),
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't create translation",
            ),
        ]
        # retrieve test cases
        self.retrieve_cases = [  # (current_user, to_retrieve, response_status, info_msg)
            (self.superuser, self.translation, status.HTTP_200_OK, "SUPERUSER can see translation"),
            (self.admin, self.translation, status.HTTP_403_FORBIDDEN, "ADMIN can't see translation"),
            (self.manager, self.translation, status.HTTP_403_FORBIDDEN, "MANAGER can't see translation"),
            (
                self.superuser,
                self.other_translation,
                status.HTTP_200_OK,
                "SUPERUSER can see other translation",
            ),
        ]
        # update test cases
        self.update_cases = [  # (who_requested, to_update, payload, response_status, info_msg)
            (
                self.superuser,
                self.translation,
                self.build_put_data(self.translation),
                status.HTTP_200_OK,
                "SUPERUSER can update his translation",
            ),
            (
                self.superuser,
                self.other_translation,
                self.build_put_data(self.other_translation),
                status.HTTP_200_OK,
                "SUPERUSER can update other translation",
            ),
            (
                self.admin,
                self.translation,
                self.build_put_data(self.translation),
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't update translation at all",
            ),
            (
                self.manager,
                self.translation,
                self.build_put_data(self.translation),
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't update translation at all",
            ),
        ]
        # delete test_cases
        self.delete_cases = [  # (who_requested, to_delete, response_status, info_msg)
            (
                self.admin,
                self.translation,
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't delete translation at all",
            ),
            (
                self.manager,
                self.translation,
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't delete translation at all",
            ),
            (
                self.superuser,
                self.translation,
                status.HTTP_204_NO_CONTENT,
                "SUPERUSER can delete his translation",
            ),
            (
                self.superuser,
                self.other_translation,
                status.HTTP_204_NO_CONTENT,
                "SUPERUSER can delete other translation",
            ),
        ]
        # action /add test cases
        self.action_create_info_cases = [
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see action /add"),
            (self.admin, status.HTTP_403_FORBIDDEN, "ADMIN can't see action /add"),
            (self.manager, status.HTTP_403_FORBIDDEN, "MANAGER can't see action /add"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see action /add"),
        ]
        # action /ids test cases
        self.action_multiple_delete_get_cases = [
            (self.superuser, status.HTTP_400_BAD_REQUEST, "SUPERUSER can see action /ids"),
            (self.admin, status.HTTP_403_FORBIDDEN, "ADMIN can't see action /ids"),
            (self.manager, status.HTTP_403_FORBIDDEN, "MANAGER can't see action /ids"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see action /ids"),
        ]
        self.action_multiple_delete_post_cases = [
            (
                self.superuser,
                {"ids": [1, 2, 3]},
                status.HTTP_204_NO_CONTENT,
                "SUPERUSER can delete multiple",
            ),
            (
                self.admin,
                {"ids": [1, 2, 3]},
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't delete multiple",
            ),
            (
                self.manager,
                {"ids": [1, 2, 3]},
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't delete multiple",
            ),
        ]

    def build_post_data(self, optional: dict = None):
        data = {
            "key": self.fake.word(),
            "value": self.fake.sentence(nb_words=2),
        }
        if optional:
            data.update(optional)
        return data

    def build_put_data(self, instance: ProductTranslation, optional: dict = None):
        data = {
            "key": instance.key,
            "value": self.fake.sentence(nb_words=2),
        }
        if optional:
            data.update(optional)
        return data

    def test_list(self):
        self.get_request_factory(self.urls["list"], self.list_cases)

    def test_create(self):
        self.post_request_factory(self.urls["list"], self.create_cases)

    def test_retrieve(self):
        self.retrieve_request_factory(self.urls["detail_raw"], self.retrieve_cases)

    def test_update(self):
        self.put_request_factory(self.urls["detail_raw"], self.update_cases)

    def test_delete(self):
        self.delete_request_factory(self.urls["detail_raw"], self.delete_cases)

    def test_action_create_info(self):
        self.get_request_factory(self.urls["add"], self.action_create_info_cases)

    def test_action_add_response(self):
        self.authorize(self.superuser)
        response = self.client.get(self.urls["add"])
        response_obj = response.data
        # Test response
        self.assertEqual(len(response_obj), 2)
        self.assertIn("key", response_obj)
        self.assertIn("value", response_obj)

    def test_action_multiple_delete_get(self):
        self.get_request_factory(self.urls["ids"], self.action_multiple_delete_get_cases)

    def test_action_multiple_delete_post(self):
        self.post_request_factory(self.urls["ids"], self.action_multiple_delete_post_cases)
