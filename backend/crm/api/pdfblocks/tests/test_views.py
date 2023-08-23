from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from faker import Faker
from rest_framework import status

from crm.api.utils import APITestCaseForChads
from crm.companies.tests.factories import CompanyFactory, CompanyMemberFactory
from crm.documents.tests.factories import PDFBlock, PDFBlockFactory
from crm.users.tests.factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory


class PDFBlockViewsetTests(APITestCaseForChads):
    def setUp(self):
        super().setUp()
        # test data
        self.fake = Faker(locale="ru_RU")
        self.credentials = {"password": "secretpass123"}
        self.image = open("crm/static/img/tests/img_150x150.png", "rb").read()
        # create users
        self.superuser = SuperUserFactory(**self.credentials)
        self.admin = AdminUserFactory(**self.credentials)
        self.manager = ManagerUserFactory(**self.credentials)
        self.other_superuser = SuperUserFactory(**self.credentials)
        # create companies
        self.company = CompanyFactory()
        self.other_company = CompanyFactory()
        # create company pdf blocks
        self.pdf_block = PDFBlockFactory(company=self.company)
        self.pdf_block_1 = PDFBlockFactory(company=self.company)
        self.other_pdf_block = PDFBlockFactory(company=self.other_company)
        # Create company memberships
        self.member_superuser = CompanyMemberFactory(user=self.superuser, company=self.company)
        self.member_admin = CompanyMemberFactory(user=self.admin, company=self.company)
        self.member_manager = CompanyMemberFactory(user=self.manager, company=self.company)
        self.member_other = CompanyMemberFactory(user=self.other_superuser, company=self.other_company)
        # urls
        self.urls = {
            "list": reverse("api:pdfblock-list"),
            "detail": reverse("api:pdfblock-detail", args=[self.pdf_block.id]),
            "detail_raw": "api:pdfblock-detail",
            "add": reverse("api:pdfblock-add"),
            "ids": reverse("api:pdfblock-ids"),
        }
        # list test cases
        self.list_cases = [  # (current_user, response_status, info_msg)
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see pdf blocks"),
            (self.admin, status.HTTP_200_OK, "ADMIN can see pdf blocks"),
            (self.manager, status.HTTP_403_FORBIDDEN, "MANAGER can see pdf blocks"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see pdf blocks"),
        ]
        # create test cases
        self.create_cases = [  # (current_user, to_create, response_status, info_msg)
            (
                self.superuser,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "SUPERUSER can create pdf block",
            ),
            (
                self.superuser,
                self.build_post_data(optional={"company": self.other_company.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can't create pdf block with other company",
            ),
            (
                self.admin,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "ADMIN can create pdf block",
            ),
            (
                self.admin,
                self.build_post_data(optional={"company": self.other_company.id}),
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't create pdf block with other company",
            ),
            (
                self.manager,
                self.build_post_data(),
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't create pdf block",
            ),
        ]
        # retrieve test cases
        self.retrieve_cases = [  # (current_user, to_retrieve, response_status, info_msg)
            (self.superuser, self.pdf_block, status.HTTP_200_OK, "SUPERUSER can see pdf block"),
            (self.admin, self.pdf_block, status.HTTP_200_OK, "ADMIN can see pdf block"),
            (self.manager, self.pdf_block, status.HTTP_403_FORBIDDEN, "MANAGER can see pdf block"),
            (
                self.superuser,
                self.other_pdf_block,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't see other pdf block",
            ),
            (
                self.admin,
                self.other_pdf_block,
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't see other pdf block",
            ),
        ]
        # update test cases
        self.update_cases = [  # (who_requested, to_update, payload, response_status, info_msg)
            (
                self.superuser,
                self.pdf_block,
                self.build_put_data(self.pdf_block),
                status.HTTP_200_OK,
                "SUPERUSER can update his pdf block",
            ),
            (
                self.superuser,
                self.pdf_block,
                self.build_put_data(self.pdf_block, optional={"company": self.other_company.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can't update his pdf block with other company",
            ),
            (
                self.admin,
                self.pdf_block,
                self.build_put_data(self.pdf_block),
                status.HTTP_200_OK,
                "ADMIN can update his pdf block",
            ),
            (
                self.superuser,
                self.other_pdf_block,
                self.build_put_data(self.other_pdf_block),
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't update other pdf block",
            ),
            (
                self.admin,
                self.other_pdf_block,
                self.build_put_data(self.other_pdf_block),
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't update other pdf block",
            ),
        ]
        # delete test_cases
        self.delete_cases = [  # (who_requested, to_delete, response_status, info_msg)
            (
                self.admin,
                self.pdf_block_1,
                status.HTTP_204_NO_CONTENT,
                "ADMIN can delete his pdf block",
            ),
            (
                self.manager,
                self.pdf_block,
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't delete his pdf block",
            ),
            (
                self.superuser,
                self.pdf_block,
                status.HTTP_204_NO_CONTENT,
                "SUPERUSER can delete his pdf block",
            ),
            (
                self.superuser,
                self.other_pdf_block,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't delete other pdf block",
            ),
            (
                self.admin,
                self.other_pdf_block,
                status.HTTP_404_NOT_FOUND,
                "ADMIN can't delete other pdf block",
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

    def build_post_data(self, optional: dict = None):
        image_file = SimpleUploadedFile("image.jpg", self.image, content_type="image/jpeg")
        data = {
            "company": self.company.id,
            "name": self.fake.sentence(nb_words=4),
            "text": self.fake.paragraph(),
            "image": image_file,
        }
        if optional:
            data.update(optional)
        return data

    def build_put_data(self, instance: PDFBlock, optional: dict = None) -> dict:
        data = {
            "company": instance.company.id,
            "name": self.fake.sentence(nb_words=4),
            "text": self.fake.paragraph(),
        }
        if optional:
            data.update(optional)
        return data

    def test_list(self):
        self.get_request_factory(self.urls["list"], self.list_cases)

    def test_create(self):
        self.post_request_factory(self.urls["list"], self.create_cases, multipart=True)

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
