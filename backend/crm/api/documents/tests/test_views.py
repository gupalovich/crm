from django.urls import reverse
from faker import Faker
from rest_framework import status

from crm.api.utils import APITestCaseForChads
from crm.companies.tests.factories import CompanyFactory, CompanyMemberFactory
from crm.documents.tests.factories import Document, DocumentFactory, ProductFactory
from crm.users.tests.factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory


class DocumentViewsetTests(APITestCaseForChads):
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
        # create products
        self.product = ProductFactory(company=self.company)
        self.other_product = ProductFactory(company=self.other_company)
        # create documents
        self.document = DocumentFactory(product=self.product)
        self.document_1 = DocumentFactory(product=self.product)
        self.other_document = DocumentFactory(product=self.other_product)
        # Create company memberships
        self.member_superuser = CompanyMemberFactory(user=self.superuser, company=self.company)
        self.member_admin = CompanyMemberFactory(user=self.admin, company=self.company)
        self.member_manager = CompanyMemberFactory(user=self.manager, company=self.company)
        self.member_other = CompanyMemberFactory(user=self.other_superuser, company=self.other_company)
        # urls
        self.urls = {
            "list": reverse("api:document-list"),
            "detail": reverse("api:document-detail", args=[self.document.id]),
            "detail_raw": "api:document-detail",
            "ids": reverse("api:document-ids"),
        }
        # list test cases
        self.list_cases = [  # (current_user, response_status, info_msg)
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see documents"),
            (self.admin, status.HTTP_200_OK, "ADMIN can see documents"),
            (self.manager, status.HTTP_200_OK, "MANAGER can see documents"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see documents"),
        ]
        # retrieve test cases
        self.retrieve_cases = [  # (current_user, to_retrieve, response_status, info_msg)
            (self.superuser, self.document, status.HTTP_200_OK, "SUPERUSER can see document"),
            (self.admin, self.document, status.HTTP_200_OK, "ADMIN can see document"),
            (self.manager, self.document, status.HTTP_200_OK, "MANAGER can see document"),
            (
                self.superuser,
                self.other_document,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't see other document",
            ),
            (
                self.admin,
                self.other_document,
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't see other document",
            ),
            (
                self.manager,
                self.other_document,
                status.HTTP_404_NOT_FOUND,
                "MANAGER can't see other document",
            ),
        ]
        # update test cases
        self.update_cases = [  # (who_requested, to_update, payload, response_status, info_msg)
            (
                self.superuser,
                self.document,
                self.build_put_data(self.document),
                status.HTTP_200_OK,
                "SUPERUSER can update his document",
            ),
            (
                self.admin,
                self.document,
                self.build_put_data(self.document),
                status.HTTP_200_OK,
                "ADMIN can update his document",
            ),
            (
                self.manager,
                self.document,
                self.build_put_data(self.document),
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't update his document",
            ),
            (
                self.superuser,
                self.other_document,
                self.build_put_data(self.other_document),
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't update other document",
            ),
            (
                self.admin,
                self.other_document,
                self.build_put_data(self.other_document),
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't update other document",
            ),
        ]

        # delete test_cases
        self.delete_cases = [  # (who_requested, to_delete, response_status, info_msg)
            (
                self.admin,
                self.document_1,
                status.HTTP_204_NO_CONTENT,
                "ADMIN can delete his document",
            ),
            (
                self.manager,
                self.document,
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't delete his document",
            ),
            (
                self.superuser,
                self.document,
                status.HTTP_204_NO_CONTENT,
                "SUPERUSER can delete his document",
            ),
            (
                self.superuser,
                self.other_document,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't delete other document",
            ),
            (
                self.admin,
                self.other_document,
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't delete other document",
            ),
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
                status.HTTP_204_NO_CONTENT,
                "ADMIN can delete multiple",
            ),
            (
                self.manager,
                {"ids": [1, 2, 3]},
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't delete multiple",
            ),
        ]

    def build_put_data(self, instance: Document, optional: dict = None) -> dict:
        data = {
            "name": self.fake.sentence(nb_words=4),
        }
        if optional:
            data.update(optional)
        return data

    def test_list(self):
        self.get_request_factory(self.urls["list"], self.list_cases)

    def test_retrieve(self):
        self.retrieve_request_factory(self.urls["detail_raw"], self.retrieve_cases)

    def test_update(self):
        self.put_request_factory(self.urls["detail_raw"], self.update_cases)

    def test_delete(self):
        self.delete_request_factory(self.urls["detail_raw"], self.delete_cases)

    def test_action_multiple_delete_get(self):
        self.get_request_factory(self.urls["ids"], self.action_multiple_delete_get_cases)

    def test_action_multiple_delete_post(self):
        self.post_request_factory(self.urls["ids"], self.action_multiple_delete_post_cases)
