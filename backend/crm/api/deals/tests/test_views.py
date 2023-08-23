from django.urls import reverse
from faker import Faker
from rest_framework import status

from crm.api.utils import APITestCaseForChads
from crm.companies.tests.factories import (
    CompanyFactory,
    CompanyMemberFactory,
    Customer,
    CustomerFactory,
    Deal,
    DealFactory,
    ProductFactory,
)
from crm.users.tests.factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory


class DealViewsetTests(APITestCaseForChads):
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
        # create deals
        self.product = ProductFactory(company=self.company)
        self.product_1 = ProductFactory(company=self.company)
        self.other_product = ProductFactory(company=self.other_company)
        self.deal = DealFactory(manager=self.manager, product=self.product)
        self.deal_1 = DealFactory(manager=self.manager, product=self.product)
        self.other_deal = DealFactory(manager=self.other_superuser, product=self.other_product)
        # create customers
        self.customer = CustomerFactory(company=self.company)
        self.other_customer = CustomerFactory(company=self.other_company)
        # Create company memberships
        self.member_superuser = CompanyMemberFactory(user=self.superuser, company=self.company)
        self.member_admin = CompanyMemberFactory(user=self.admin, company=self.company)
        self.member_manager = CompanyMemberFactory(user=self.manager, company=self.company)
        self.member_other = CompanyMemberFactory(user=self.other_superuser, company=self.other_company)
        # urls
        self.urls = {
            "list": reverse("api:deal-list"),
            "detail": reverse("api:deal-detail", args=[self.deal.id]),
            "detail_raw": "api:deal-detail",
            "add": reverse("api:deal-add"),
            "ids": reverse("api:deal-ids"),
        }
        # list test cases
        self.list_cases = [  # (current_user, response_status, info_msg)
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see deals"),
            (self.admin, status.HTTP_200_OK, "ADMIN can see deals"),
            (self.manager, status.HTTP_200_OK, "MANAGER can see deals"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see deals"),
        ]
        # create test cases
        self.create_cases = [  # (current_user, to_create, response_status, info_msg)
            (
                self.superuser,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "SUPERUSER can create deals",
            ),
            (
                self.superuser,
                self.build_post_data(optional={"product": self.other_product.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can't create deal with other product company",
            ),
            (
                self.superuser,
                self.build_post_data().pop("product"),
                status.HTTP_400_BAD_REQUEST,
                "Can't create deal without product id",
            ),
            (
                self.superuser,
                self.build_post_data().pop("customer"),
                status.HTTP_400_BAD_REQUEST,
                "Can't create deal without customer id",
            ),
            (
                self.admin,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "ADMIN can create deal",
            ),
            (
                self.manager,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "MANAGER can create deal",
            ),
        ]
        # retrieve test cases
        self.retrieve_cases = [  # (current_user, to_retrieve, response_status, info_msg)
            (self.superuser, self.deal, status.HTTP_200_OK, "SUPERUSER can see deal"),
            (self.admin, self.deal, status.HTTP_200_OK, "ADMIN can see deal"),
            (self.manager, self.deal, status.HTTP_200_OK, "MANAGER can see deal"),
            (
                self.superuser,
                self.other_deal,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't see other deal",
            ),
            (
                self.admin,
                self.other_deal,
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't see other deal",
            ),
            (
                self.manager,
                self.other_deal,
                status.HTTP_404_NOT_FOUND,
                "MANAGER can't see other deal",
            ),
        ]
        # update test cases
        self.update_cases = [  # (who_requested, to_update, payload, response_status, info_msg)
            (
                self.superuser,
                self.deal,
                self.build_put_data(self.deal),
                status.HTTP_200_OK,
                "SUPERUSER can update deal",
            ),
            (
                self.superuser,
                self.deal,
                self.build_put_data(self.deal, optional={"product": self.other_product.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can't update his deal with other product",
            ),
            (
                self.superuser,
                self.deal,
                self.build_put_data(self.deal, optional={"customer": self.other_customer.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can't update his deal with other customer",
            ),
            (
                self.admin,
                self.deal,
                self.build_put_data(self.deal),
                status.HTTP_200_OK,
                "ADMIN can update deal",
            ),
            (
                self.manager,
                self.deal,
                self.build_put_data(self.deal),
                status.HTTP_200_OK,
                "MANAGER can update deal",
            ),
            (
                self.superuser,
                self.other_deal,
                self.build_put_data(self.other_deal),
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't update other deal",
            ),
            (
                self.admin,
                self.other_deal,
                self.build_put_data(self.other_deal),
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't update other deal",
            ),
            (
                self.manager,
                self.other_deal,
                self.build_put_data(self.other_deal),
                status.HTTP_404_NOT_FOUND,
                "MANAGER can't update other deal",
            ),
        ]
        # delete test_cases
        self.delete_cases = [  # (who_requested, to_delete, response_status, info_msg)
            (self.admin, self.deal_1, status.HTTP_204_NO_CONTENT, "ADMIN can delete his deal"),
            (self.manager, self.deal, status.HTTP_403_FORBIDDEN, "MANAGER can't delete his deal"),
            (self.superuser, self.deal, status.HTTP_204_NO_CONTENT, "SUPERUSER can delete his deal"),
            (self.superuser, self.other_deal, status.HTTP_404_NOT_FOUND, "SUPERUSER can't delete other deal"),
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
            "product": self.product.id,
            "customer": {
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "email": self.fake.email(),
                "phone_number": self.fake.phone_number(),
            },
        }
        if optional:
            data.update(optional)
        return data

    def build_put_data(self, instance: Deal, optional: dict = None):
        data = {
            "product": self.product_1.id,
            "customer": self.customer.id,
        }
        if optional:
            data.update(optional)
        return data

    def test_list(self):
        self.get_request_factory(self.urls["list"], self.list_cases)

    def test_create(self):
        init_count = Customer.objects.count()
        self.post_request_factory(self.urls["list"], self.create_cases)
        self.assertGreater(Customer.objects.count(), init_count)

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
