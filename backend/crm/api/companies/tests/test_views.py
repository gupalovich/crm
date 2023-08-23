from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from faker import Faker
from rest_framework import status

from crm.api.utils import APITestCaseForChads
from crm.companies.tests.factories import Company, CompanyFactory, CompanyMemberFactory, CompanyTypeFactory
from crm.users.tests.factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory


class CompanyViewsetTests(APITestCaseForChads):
    def setUp(self):
        super().setUp()
        # test data
        self.fake = Faker()
        self.credentials = {"password": "secretpass123"}
        self.image = open("crm/static/img/tests/img_150x150.png", "rb").read()
        # create users
        self.superuser = SuperUserFactory(**self.credentials)
        self.admin = AdminUserFactory(**self.credentials)
        self.manager = ManagerUserFactory(**self.credentials)
        self.other_superuser = SuperUserFactory(**self.credentials)
        # create companies
        self.company_type = CompanyTypeFactory()
        self.other_company_type = CompanyTypeFactory()
        self.company = CompanyFactory(company_type=self.company_type)
        self.other_company = CompanyFactory(company_type=self.other_company_type)
        # Create company memberships
        self.member_superuser = CompanyMemberFactory(user=self.superuser, company=self.company)
        self.member_admin = CompanyMemberFactory(user=self.admin, company=self.company)
        self.member_manager = CompanyMemberFactory(user=self.manager, company=self.company)
        self.member_other = CompanyMemberFactory(user=self.other_superuser, company=self.other_company)
        # urls
        self.urls = {
            "list": reverse("api:company-list"),
            "detail": reverse("api:company-detail", args=[self.company.id]),
            "detail_raw": "api:company-detail",
            "add": reverse("api:company-add"),
        }
        # list test cases
        self.list_cases = [  # (current_user, response_status, info_msg)
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see companies list"),
            (self.admin, status.HTTP_200_OK, "ADMIN can see companies list"),
            (self.manager, status.HTTP_403_FORBIDDEN, "MANAGER can't see companies list"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see companies list"),
        ]
        # create test cases
        self.create_cases = [  # (current_user, to_create, response_status, info_msg)
            (
                self.superuser,
                self.build_post_data(),
                status.HTTP_201_CREATED,
                "SUPERUSER can create company",
            ),
            (
                self.superuser,
                self.build_post_data(optional={"company_type": self.other_company_type.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can't create company with other company type",
            ),
            (
                self.admin,
                self.build_post_data(),
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't create company",
            ),
        ]
        # retrieve test cases
        self.retrieve_cases = [  # (current_user, to_retrieve, response_status, info_msg)
            (self.superuser, self.company, status.HTTP_200_OK, "SUPERUSER can see company"),
            (self.admin, self.company, status.HTTP_200_OK, "ADMIN can see company"),
            (self.manager, self.company, status.HTTP_403_FORBIDDEN, "MANAGER can't see company"),
            (
                self.superuser,
                self.other_company,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't see other_company",
            ),
            (self.admin, self.other_company, status.HTTP_404_NOT_FOUND, "ADMIN can't see other_company"),
            (
                self.manager,
                self.other_company,
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't see other_company",
            ),
        ]
        # update test cases
        self.update_cases = [  # (who_requested, to_update, payload, response_status, info_msg)
            (
                self.superuser,
                self.company,
                self.build_put_data(self.company),
                status.HTTP_200_OK,
                "SUPERUSER can update his company",
            ),
            (
                self.superuser,
                self.company,
                self.build_put_data(self.company, optional={"company_type": self.other_company_type.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can't update his company with other company_type",
            ),
            (
                self.superuser,
                self.other_company,
                self.build_put_data(self.other_company),
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't update other company",
            ),
            (
                self.admin,
                self.company,
                self.build_put_data(self.company),
                status.HTTP_200_OK,
                "ADMIN can update his company",
            ),
        ]
        # delete test_cases
        self.delete_cases = [  # (who_requested, to_delete, response_status, info_msg)
            (self.admin, self.company, status.HTTP_403_FORBIDDEN, "ADMIN can't delete his company"),
            (self.manager, self.company, status.HTTP_403_FORBIDDEN, "MANAGER can't delete his company"),
            (
                self.superuser,
                self.company,
                status.HTTP_204_NO_CONTENT,
                "SUPERUSER can delete his company",
            ),
            (
                self.superuser,
                self.other_company,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't delete other company",
            ),
        ]
        # action /add test cases
        self.action_create_info_cases = [
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see action /add"),
            (self.admin, status.HTTP_200_OK, "ADMIN can see action /add"),
            (self.manager, status.HTTP_200_OK, "MANAGER can see action /add"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see action /add"),
        ]

    def build_post_data(self, optional: dict = None):
        image_file = SimpleUploadedFile("image.jpg", self.image, content_type="image/jpeg")
        data = {
            "company_type": self.company_type.id,
            "name": self.fake.company(),
            "executive_name": self.fake.name(),
            "executive_position": self.fake.job(),
            "address": self.company.address,
            "logo_image": image_file,
            "business_card": "{first_name} {last_name}",
        }
        if optional:
            data.update(optional)
        return data

    def build_put_data(self, instance: Company, optional: dict = None):
        image_file = SimpleUploadedFile("image.jpg", self.image, content_type="image/jpeg")
        data = {
            "company_type": self.company_type.id,
            "name": self.fake.company(),
            "executive_name": self.fake.name(),
            "executive_position": self.fake.job(),
            "address": instance.address,
            "logo_image": image_file,
            "business_card": "{first_name} {last_name}",
        }
        if optional:
            data.update(optional)
        return data

    def test_list(self):
        self.get_request_factory(self.urls["list"], self.list_cases)

    def test_list_response(self):
        self.authorize(self.superuser)
        # Test response
        response = self.client.get(self.urls["list"])
        response_obj = response.data
        self.assertIn("items", response_obj)
        self.assertEqual(response_obj["count"], 1)
        self.assertEqual(response_obj["items"][0]["name"], self.company.name)

    def test_create(self):
        self.post_request_factory(self.urls["list"], self.create_cases, multipart=True)

    def test_create_non_unique_company_raises_validation_error(self):
        self.authorize(self.superuser)
        # Test response
        payload = self.build_post_data(optional={"name": "test"})
        response = self.client.post(self.urls["list"], payload, format="multipart")
        # test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test copy response
        response = self.client.post(self.urls["list"], payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Компания с таким именем уже существует", str(response.data))

    def test_create__company_member_is_added(self):
        self.authorize(self.superuser)
        # Test response
        payload = self.build_post_data()
        response = self.client.post(self.urls["list"], payload, format="multipart")
        company = Company.objects.get(id=response.data["id"])
        company_members = company.members.values_list("user__username", flat=True)
        expected_bc = f"{self.superuser.first_name} {self.superuser.last_name}"
        self.assertEqual(len(company_members), 1)
        self.assertEqual(response.data["business_card"], expected_bc)
        self.assertIn(self.superuser.username, company_members)

    def test_retrieve(self):
        self.retrieve_request_factory(self.urls["detail_raw"], self.retrieve_cases)

    def test_update(self):
        self.put_request_factory(self.urls["detail_raw"], self.update_cases, multipart=True)

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
        self.assertIn("name", response_obj)
        self.assertIn("company_type", response_obj)
        self.assertIn("executive_name", response_obj)
        self.assertIn("executive_position", response_obj)
        self.assertIn("address", response_obj)
        self.assertIn("logo_image", response_obj)
        self.assertIn("signature_image", response_obj)
        self.assertIn("business_card", response_obj)
