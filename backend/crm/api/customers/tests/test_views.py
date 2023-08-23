from django.urls import reverse
from faker import Faker
from rest_framework import status

from crm.api.utils import APITestCaseForChads
from crm.companies.tests.factories import CompanyFactory, CompanyMemberFactory, Customer, CustomerFactory
from crm.users.tests.factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory


class CustomerViewsetTests(APITestCaseForChads):
    def setUp(self):
        super().setUp()
        # test data
        self.fake = Faker(locale="ru_RU")
        self.credentials = {"password": "secretpass123"}
        # create users
        self.superuser = SuperUserFactory(**self.credentials)
        self.admin = AdminUserFactory(**self.credentials)
        self.manager = ManagerUserFactory(**self.credentials)
        self.other_superuser = SuperUserFactory(**self.credentials)
        # create companies
        self.company = CompanyFactory()
        self.other_company = CompanyFactory()
        # create company customers
        self.customer = CustomerFactory(company=self.company)
        self.customer_1 = CustomerFactory(company=self.company)
        self.other_customer = CustomerFactory(company=self.other_company)
        # Create company memberships
        self.member_superuser = CompanyMemberFactory(user=self.superuser, company=self.company)
        self.member_admin = CompanyMemberFactory(user=self.admin, company=self.company)
        self.member_manager = CompanyMemberFactory(user=self.manager, company=self.company)
        self.member_other = CompanyMemberFactory(user=self.other_superuser, company=self.other_company)
        # urls
        self.urls = {
            "list": reverse("api:customer-list"),
            "detail": reverse("api:customer-detail", args=[self.customer.id]),
            "detail_raw": "api:customer-detail",
            "add": reverse("api:customer-add"),
            "ids": reverse("api:customer-ids"),
        }
        # list test cases
        self.list_cases = [  # (current_user, response_status, info_msg)
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see customers"),
            (self.admin, status.HTTP_200_OK, "ADMIN can see customers"),
            (self.manager, status.HTTP_200_OK, "MANAGER can see customers"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see customers"),
        ]
        # create test cases
        self.create_cases = [  # (current_user, to_create, response_status, info_msg)
            (
                self.superuser,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "SUPERUSER can create customer",
            ),
            (
                self.superuser,
                self.build_post_data(optional={"company": self.other_company.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can't create customer with other company",
            ),
            (
                self.superuser,
                self.build_post_data().pop("company"),
                status.HTTP_400_BAD_REQUEST,
                "SUPERUSER can't create customer without company id",
            ),
            (
                self.admin,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "ADMIN can create customer",
            ),
            (
                self.admin,
                self.build_post_data(optional={"company": self.other_company.id}),
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't create customer with other company",
            ),
            (
                self.manager,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "MANAGER can create customer",
            ),
            (
                self.admin,
                self.build_post_data(optional={"company": self.other_company.id}),
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't create customer with other company",
            ),
        ]
        # retrieve test cases
        self.retrieve_cases = [  # (current_user, to_retrieve, response_status, info_msg)
            (self.superuser, self.customer, status.HTTP_200_OK, "SUPERUSER can see customer"),
            (self.admin, self.customer, status.HTTP_200_OK, "ADMIN can see customer"),
            (self.manager, self.customer, status.HTTP_200_OK, "MANAGER can see customer"),
            (
                self.superuser,
                self.other_customer,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't see other customer",
            ),
            (
                self.admin,
                self.other_customer,
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't see other customer",
            ),
            (
                self.manager,
                self.other_customer,
                status.HTTP_404_NOT_FOUND,
                "MANAGER can't see other customer",
            ),
        ]
        # update test cases
        self.update_cases = [  # (who_requested, to_update, payload, response_status, info_msg)
            (
                self.superuser,
                self.customer,
                self.build_put_data(self.customer),
                status.HTTP_200_OK,
                "SUPERUSER can update his customer",
            ),
            (
                self.superuser,
                self.customer,
                self.build_put_data(self.customer, optional={"company": self.other_company.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can update his customer with other company",
            ),
            (
                self.admin,
                self.customer,
                self.build_put_data(self.customer),
                status.HTTP_200_OK,
                "ADMIN can update his customer",
            ),
            (
                self.manager,
                self.customer,
                self.build_put_data(self.customer),
                status.HTTP_200_OK,
                "MANAGER can update his customer",
            ),
            (
                self.superuser,
                self.other_customer,
                self.build_put_data(self.other_customer),
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't update other customer",
            ),
            (
                self.admin,
                self.other_customer,
                self.build_put_data(self.other_customer),
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't update other customer",
            ),
            (
                self.manager,
                self.other_customer,
                self.build_put_data(self.other_customer),
                status.HTTP_404_NOT_FOUND,
                "MANAGER can't update other customer",
            ),
        ]
        # delete test_cases
        self.delete_cases = [  # (who_requested, to_delete, response_status, info_msg)
            (self.admin, self.customer, status.HTTP_204_NO_CONTENT, "ADMIN can delete his customer"),
            (
                self.manager,
                self.customer,
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't delete his customer",
            ),
            (
                self.superuser,
                self.customer_1,
                status.HTTP_204_NO_CONTENT,
                "SUPERUSER can delete his customer",
            ),
            (
                self.superuser,
                self.other_customer,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't delete other customer",
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
            (self.admin, {"ids": [1, 2, 3]}, status.HTTP_204_NO_CONTENT, "ADMIN can delete multiple"),
            (
                self.manager,
                {"ids": [1, 2, 3]},
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't delete multiple",
            ),
        ]

    def build_post_data(self, optional: dict = None):
        data = {
            "company": self.company.id,
            "first_name": self.fake.first_name(),
            "middle_name": "",
            "last_name": self.fake.last_name(),
            "email": self.fake.email(),
            "phone_number": self.fake.phone_number(),
        }
        if optional:
            data.update(optional)
        return data

    def build_put_data(self, instance: Customer, optional: dict = None):
        data = {
            "company": self.company.id,
            "first_name": instance.first_name,
            "middle_name": self.fake.last_name(),
            "last_name": instance.last_name,
            "email": self.fake.email(),
            "phone_number": instance.phone_number,
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

    def test_action_multiple_delete_get(self):
        self.get_request_factory(self.urls["ids"], self.action_multiple_delete_get_cases)

    def test_action_multiple_delete_post(self):
        self.post_request_factory(self.urls["ids"], self.action_multiple_delete_post_cases)
