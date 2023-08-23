from django.urls import reverse
from faker import Faker
from rest_framework import status

from crm.api.utils import APITestCaseForChads
from crm.companies.tests.factories import (
    CompanyFactory,
    CompanyMemberFactory,
    CompanyType,
    CompanyTypeFactory,
)
from crm.users.tests.factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory


class CompanyTypeViewsetTests(APITestCaseForChads):
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
        # create company types
        self.company_type = CompanyTypeFactory()
        self.other_company_type = CompanyTypeFactory()
        # create companies
        self.company = CompanyFactory(company_type=self.company_type)
        self.other_company = CompanyFactory(company_type=self.other_company_type)
        # Create company memberships
        self.member_superuser = CompanyMemberFactory(user=self.superuser, company=self.company)
        self.member_admin = CompanyMemberFactory(user=self.admin, company=self.company)
        self.member_manager = CompanyMemberFactory(user=self.manager, company=self.company)
        self.member_other = CompanyMemberFactory(user=self.other_superuser, company=self.other_company)
        # urls
        self.urls = {
            "list": reverse("api:companytype-list"),
            "detail": reverse("api:companytype-detail", args=[self.company.id]),
            "detail_raw": "api:companytype-detail",
            "add": reverse("api:companytype-add"),
            "ids": reverse("api:companytype-ids"),
        }
        # list test cases
        self.list_cases = [  # (current_user, response_status, info_msg)
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see company type list"),
            (self.admin, status.HTTP_200_OK, "ADMIN can see company type list"),
            (self.manager, status.HTTP_403_FORBIDDEN, "MANAGER can't see company type list"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see company type list"),
        ]
        # create test cases
        self.create_cases = [  # (current_user, to_create, response_status, info_msg)
            (
                self.superuser,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "SUPERUSER can create company type",
            ),
            (
                self.admin,
                self.build_post_data(),
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't create company type",
            ),
        ]
        # retrieve test cases
        self.retrieve_cases = [  # (current_user, to_retrieve, response_status, info_msg)
            (self.superuser, self.company_type, status.HTTP_200_OK, "SUPERUSER can see company type"),
            (self.admin, self.company_type, status.HTTP_200_OK, "ADMIN can see company type"),
            (
                self.manager,
                self.company_type,
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't see company type",
            ),
            (
                self.superuser,
                self.other_company_type,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't see other company type",
            ),
            (
                self.admin,
                self.other_company_type,
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't see other company type",
            ),
            (
                self.manager,
                self.other_company_type,
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't see other company type",
            ),
        ]
        # update test cases
        self.update_cases = [  # (who_requested, to_update, payload, response_status, info_msg)
            (
                self.superuser,
                self.company_type,
                self.build_put_data(self.company_type),
                status.HTTP_200_OK,
                "SUPERUSER can update his company type",
            ),
            (
                self.superuser,
                self.other_company_type,
                self.build_put_data(self.other_company_type),
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't update other company type",
            ),
            (
                self.admin,
                self.company_type,
                self.build_put_data(self.company_type),
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't update company type at all",
            ),
            (
                self.manager,
                self.company_type,
                self.build_put_data(self.company_type),
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't update company type at all",
            ),
        ]
        # delete test_cases
        self.delete_cases = [  # (who_requested, to_delete, response_status, info_msg)
            (
                self.admin,
                self.company_type,
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't delete company type at all",
            ),
            (
                self.manager,
                self.company_type,
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't delete company type at all",
            ),
            (
                self.superuser,
                self.company_type,
                status.HTTP_204_NO_CONTENT,
                "SUPERUSER can delete his company type",
            ),
            (
                self.superuser,
                self.other_company_type,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't delete other company type",
            ),
        ]
        # action /add test cases
        self.action_create_info_cases = [
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see action /add"),
            (self.admin, status.HTTP_200_OK, "ADMIN can see action /add"),
            (self.manager, status.HTTP_200_OK, "MANAGER can see action /add"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see action /add"),
        ]
        # action /ids test cases
        self.action_multiple_delete_get_cases = [
            (self.superuser, status.HTTP_400_BAD_REQUEST, "SUPERUSER can see action /ids"),
            (self.admin, status.HTTP_400_BAD_REQUEST, "ADMIN can see action /ids"),
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
        data = {"name": self.fake.word()}
        if optional:
            data.update(optional)
        return data

    def build_put_data(self, instance: CompanyType, optional: dict = None):
        data = {"name": self.fake.word()}
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
        self.assertEqual(len(response_obj), 1)
        self.assertIn("name", response_obj)

    def test_action_multiple_delete_get(self):
        self.get_request_factory(self.urls["ids"], self.action_multiple_delete_get_cases)

    def test_action_multiple_delete_post(self):
        self.post_request_factory(self.urls["ids"], self.action_multiple_delete_post_cases)
