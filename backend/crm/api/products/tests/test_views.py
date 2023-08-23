from django.urls import reverse
from faker import Faker
from rest_framework import status

from crm.api.utils import APITestCaseForChads
from crm.companies.tests.factories import (
    CompanyFactory,
    CompanyMemberFactory,
    Product,
    ProductFactory,
    gen_product_data,
)
from crm.documents.tests.factories import Document
from crm.users.tests.factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory


class ProductViewsetTests(APITestCaseForChads):
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
        # create companies
        self.company = CompanyFactory()
        self.other_company = CompanyFactory()
        # create company product links
        self.product = ProductFactory(company=self.company)
        self.other_product = ProductFactory(company=self.other_company)
        # Create company memberships
        self.member_superuser = CompanyMemberFactory(user=self.superuser, company=self.company)
        self.member_admin = CompanyMemberFactory(user=self.admin, company=self.company)
        self.member_manager = CompanyMemberFactory(user=self.manager, company=self.company)
        self.member_other = CompanyMemberFactory(user=self.other_superuser, company=self.other_company)
        # urls
        self.urls = {
            "list": reverse("api:product-list"),
            "detail": reverse("api:product-detail", args=[self.product.id]),
            "detail_raw": "api:product-detail",
            "add": reverse("api:product-add"),
            "ids": reverse("api:product-ids"),
            "price": reverse("api:product-price", args=[self.product.id]),
            "offer": reverse("api:product-offer", args=[self.product.id]),
        }
        # pdf generation
        self.expected_pdf_file_name = f"{self.superuser.username}-{self.product.pk}.pdf"
        self.expected_pdf_product = self.product
        # list test cases
        self.list_cases = [  # (current_user, response_status, info_msg)
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see company product list"),
            (self.admin, status.HTTP_200_OK, "ADMIN can see company product list"),
            (self.manager, status.HTTP_200_OK, "MANAGER can see company product list"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see company product list"),
        ]
        # create test cases
        self.create_cases = [  # (current_user, to_create, response_status, info_msg)
            (
                self.superuser,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "SUPERUSER can create product",
            ),
            (
                self.superuser,
                self.build_post_data(optional={"company": self.other_company.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can't create product with other company",
            ),
            (
                self.admin,
                self.build_post_data(),
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't create product",
            ),
            (
                self.manager,
                self.build_post_data(),
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't create product",
            ),
        ]
        # retrieve test cases
        self.retrieve_cases = [  # (current_user, to_retrieve, response_status, info_msg)
            (self.superuser, self.product, status.HTTP_200_OK, "SUPERUSER can see product"),
            (self.admin, self.product, status.HTTP_200_OK, "ADMIN can see product"),
            (self.manager, self.product, status.HTTP_200_OK, "MANAGER can see product"),
            (
                self.superuser,
                self.other_product,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't see other product",
            ),
            (
                self.admin,
                self.other_product,
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't see other product",
            ),
            (
                self.manager,
                self.other_product,
                status.HTTP_404_NOT_FOUND,
                "MANAGER can't see other product",
            ),
        ]
        # update test cases
        self.update_cases = [  # (who_requested, to_update, payload, response_status, info_msg)
            (
                self.superuser,
                self.product,
                self.build_put_data(self.product),
                status.HTTP_200_OK,
                "SUPERUSER can update his product",
            ),
            (
                self.superuser,
                self.product,
                self.build_put_data(self.product, optional={"company": self.other_company.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can't update his product with other company",
            ),
            (
                self.superuser,
                self.other_product,
                self.build_put_data(self.other_product),
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't update other product",
            ),
            (
                self.admin,
                self.product,
                self.build_put_data(self.product),
                status.HTTP_200_OK,
                "ADMIN can update his product",
            ),
            (
                self.manager,
                self.product,
                self.build_put_data(self.product),
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't update his product",
            ),
        ]
        # delete test_cases
        self.delete_cases = [  # (who_requested, to_delete, response_status, info_msg)
            (
                self.admin,
                self.product,
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't delete his product",
            ),
            (
                self.manager,
                self.product,
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't delete his product",
            ),
            (
                self.superuser,
                self.product,
                status.HTTP_204_NO_CONTENT,
                "SUPERUSER can delete his product",
            ),
            (
                self.superuser,
                self.other_product,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't delete other product",
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
            (self.manager, status.HTTP_400_BAD_REQUEST, "MANAGER can see action /ids"),
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
            "company": self.company.id,
            "pid": self.fake.uuid4(),
            "name": self.fake.sentence(nb_words=3),
            "data": gen_product_data(),
            "price": self.fake.pyint(min_value=1000000, max_value=1000000000),
            "price_special": self.fake.pyint(min_value=1000000, max_value=1000000000),
            "url": self.fake.url(),
        }
        if optional:
            data.update(optional)
        return data

    def build_put_data(self, instance: Product, optional: dict = None):
        data = {
            "company": instance.company.id,
            "pid": self.fake.uuid4(),
            "name": self.fake.sentence(nb_words=3),
            "data": "",
            "price": instance.price,
            "price_special": instance.price_special,
            "url": instance.url,
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
        self.assertEqual(len(response_obj), 8)

    def test_action_multiple_delete_get(self):
        self.get_request_factory(self.urls["ids"], self.action_multiple_delete_get_cases)

    def test_action_multiple_delete_post(self):
        self.post_request_factory(self.urls["ids"], self.action_multiple_delete_post_cases)

    def test_action_price_get(self):
        self.authorize(self.superuser)
        response = self.client.get(self.urls["price"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(self.expected_pdf_file_name, response["Content-Disposition"])

    def test_action_price_post(self):
        self.authorize(self.superuser)
        response = self.client.post(self.urls["price"])
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_action_offer_get(self):
        self.authorize(self.superuser)
        response = self.client.get(self.urls["offer"])
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_action_offer_post(self):
        self.authorize(self.superuser)
        expected_name = "document name"
        payload = {"name": expected_name, "pdf_blocks": [1, 2, 3]}
        response = self.client.post(self.urls["offer"], data=payload)
        # test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test document
        self.assertEqual(Document.objects.count(), 1)
        document = Document.objects.first()
        self.assertEqual(expected_name, document.name)
        self.assertIn(self.expected_pdf_file_name, str(document.url))
        self.assertEqual(self.expected_pdf_product, document.product)
