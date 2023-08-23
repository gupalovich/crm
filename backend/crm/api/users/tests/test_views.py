from django.contrib.auth import get_user_model
from django.urls import reverse
from faker import Faker
from rest_framework import status

from crm.api.utils import APITestCaseForChads
from crm.companies.tests.factories import CompanyFactory, CompanyMemberFactory
from crm.users.tests.factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory

User = get_user_model()
SUPERUSER = User.Roles.SUPERUSER
ADMIN = User.Roles.ADMIN
MANAGER = User.Roles.MANAGER


class UserViewsetTestCase(APITestCaseForChads):
    def setUp(self):
        super().setUp()
        # test data
        self.fake = Faker(locale="ru_RU")
        self.credentials = {"password": "secretpass123"}
        # create users
        self.superuser = SuperUserFactory(**self.credentials)
        self.admin = AdminUserFactory(**self.credentials)
        self.manager = ManagerUserFactory(**self.credentials)
        self.manager_2 = ManagerUserFactory(**self.credentials)
        self.other_user = AdminUserFactory(**self.credentials)
        # create companies
        self.company = CompanyFactory()
        self.other_company = CompanyFactory()
        self.member_superuser = CompanyMemberFactory(company=self.company, user=self.superuser)
        self.member_admin = CompanyMemberFactory(company=self.company, user=self.admin)
        self.member_manager = CompanyMemberFactory(company=self.company, user=self.manager)
        self.member_manager_2 = CompanyMemberFactory(company=self.company, user=self.manager_2)
        # urls
        self.urls = {
            "list": reverse("api:user-list"),
            "detail_raw": "api:user-detail",
            "me": reverse("api:user-me"),
            "add": reverse("api:user-add"),
        }
        # list test cases
        self.list_cases = [  # (current_user, reponse_code, info_msg)
            (self.superuser, status.HTTP_200_OK, "SUPERUSER can see user list"),
            (self.admin, status.HTTP_200_OK, "ADMIN can see user list"),
            (self.manager, status.HTTP_403_FORBIDDEN, "MANAGER can't see user list"),
            (None, status.HTTP_403_FORBIDDEN, "Anonymous can't see user list"),
        ]
        # create test cases
        self.create_cases = [  # (current_user, to_create, response_status, info_msg)
            (
                self.superuser,
                self.build_post_data(optional={"role": ADMIN, "company": self.company.id}),
                status.HTTP_201_CREATED,
                "SUPERUSER can create ADMIN users",
            ),
            (
                self.admin,
                self.build_post_data(optional={"role": MANAGER, "company": self.company.id}),
                status.HTTP_201_CREATED,
                "ADMIN can create MANAGER users",
            ),
            # Invalid cases
            (
                self.superuser,
                self.build_post_data(optional={"role": ADMIN, "company": self.other_company.id}),
                status.HTTP_403_FORBIDDEN,
                "SUPERUSER can't create user and company membership if not a company member",
            ),
            (
                self.admin,
                self.build_post_data(optional={"role": MANAGER, "company": self.other_company.id}),
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't create user and company membership if not a company member",
            ),
            (
                self.superuser,
                self.build_post_data(optional={"role": ADMIN}),
                status.HTTP_400_BAD_REQUEST,
                "Company ID is required in User creation",
            ),
            (
                self.superuser,
                self.build_post_data(optional={"role": SUPERUSER, "company": self.company.id}),
                status.HTTP_400_BAD_REQUEST,
                "SUPERUSER can't create SUPERUSER users",
            ),
            (
                self.superuser,
                self.build_post_data(optional={"role": "invalid", "company": self.company.id}),
                status.HTTP_400_BAD_REQUEST,
                "SUPERUSER can't create user with invalid role",
            ),
            (
                self.admin,
                self.build_post_data(optional={"role": ADMIN, "company": self.company.id}),
                status.HTTP_400_BAD_REQUEST,
                "ADMIN can't create ADMIN users",
            ),
            (
                self.manager,
                self.build_post_data(optional={"role": MANAGER, "company": self.company.id}),
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't create users",
            ),
        ]
        # retrieve test cases
        self.retrieve_cases = [  # (current_user, to_retrieve, response_status, info_msg)
            (self.superuser, self.superuser, status.HTTP_200_OK, "SUPERUSER can see SELF"),
            (self.superuser, self.admin, status.HTTP_200_OK, "SUPERUSER can see ADMIN"),
            (self.superuser, self.manager, status.HTTP_200_OK, "SUPERUSER can see MANAGER"),
            (self.superuser, self.other_user, status.HTTP_404_NOT_FOUND, "SUPERUSER can't see other"),
            (self.admin, self.superuser, status.HTTP_403_FORBIDDEN, "ADMIN can't see SUPERUSER"),
            (self.admin, self.admin, status.HTTP_200_OK, "ADMIN can see SELF"),
            (self.admin, self.manager, status.HTTP_200_OK, "ADMIN can see MANAGER"),
            (self.admin, self.other_user, status.HTTP_404_NOT_FOUND, "ADMIN can't see other"),
            (self.manager, self.manager, status.HTTP_403_FORBIDDEN, "MANAGER can't see any user"),
        ]
        # update test cases
        self.update_cases = [  # (who_requested, to_update, payload, response_status, info_msg)
            (
                self.superuser,
                self.admin,
                self.build_put_data(self.admin),
                status.HTTP_200_OK,
                "SUPERUSER can update ADMIN",
            ),
            (
                self.superuser,
                self.manager,
                self.build_put_data(self.manager),
                status.HTTP_200_OK,
                "SUPERUSER can update MANAGER",
            ),
            (
                self.superuser,
                self.superuser,
                self.build_put_data(self.superuser),
                status.HTTP_200_OK,
                "SUPERUSER can update SELF",
            ),
            (
                self.admin,
                self.manager,
                self.build_put_data(self.manager),
                status.HTTP_200_OK,
                "ADMIN can update MANAGER",
            ),
            (
                self.admin,
                self.admin,
                self.build_put_data(self.admin),
                status.HTTP_200_OK,
                "ADMIN can update SELF",
            ),
            (
                self.admin,
                self.superuser,
                self.build_put_data(self.superuser),
                status.HTTP_403_FORBIDDEN,
                "ADMIN can't update SUPERUSER",
            ),
            (
                self.manager,
                self.admin,
                self.build_put_data(self.admin),
                status.HTTP_403_FORBIDDEN,
                "MANAGER can't update at all",
            ),
        ]
        # delete test_cases
        self.delete_cases = [  # (who_requested, to_delete, response_status, info_msg)
            (self.manager, self.admin, status.HTTP_403_FORBIDDEN, "MANAGER can't delete at all"),
            (self.other_user, self.admin, status.HTTP_404_NOT_FOUND, "OTHER can't delete ADMIN"),
            (self.other_user, self.manager, status.HTTP_404_NOT_FOUND, "OTHER can't delete MANAGER"),
            (self.admin, self.manager_2, status.HTTP_204_NO_CONTENT, "ADMIN can delete MANAGER"),
            (self.admin, self.admin, status.HTTP_403_FORBIDDEN, "ADMIN can delete SELF"),
            (
                self.superuser,
                self.other_user,
                status.HTTP_404_NOT_FOUND,
                "SUPERUSER can't delete OTHER user",
            ),
            (self.superuser, self.manager, status.HTTP_204_NO_CONTENT, "SUPERUSER can delete MANAGER"),
            (self.superuser, self.superuser, status.HTTP_204_NO_CONTENT, "SUPERUSER can delete SELF"),
        ]
        # action /add, /me test cases
        self.action_add_me_cases = [
            (self.superuser, status.HTTP_200_OK),
            (self.admin, status.HTTP_200_OK),
            (self.manager, status.HTTP_200_OK),
            (None, status.HTTP_403_FORBIDDEN),
        ]

    def build_post_data(self, optional: dict = None):
        data = {
            "username": self.fake.user_name(),
            "password": "secretpass123",
            "first_name": self.fake.first_name(),
            "middle_name": "",
            "last_name": self.fake.last_name(),
            "email": self.fake.email(),
            "phone_number": self.fake.phone_number(),
            "role": ADMIN,
        }
        if optional:
            data.update(optional)
        return data

    def build_put_data(self, instance: User, optional: dict = None):
        data = {
            # new
            "first_name": self.fake.first_name(),
            "email": self.fake.email(),
            # original
            "username": instance.username,
            "middle_name": instance.middle_name,
            "last_name": instance.last_name,
            "phone_number": instance.phone_number,
            "role": instance.role,
            "is_active": instance.is_active,
        }
        if optional:
            data.update(optional)
        return data

    def test_list(self):
        self.get_request_factory(self.urls["list"], self.list_cases)

    def test_create(self):
        self.post_request_factory(self.urls["list"], self.create_cases)

    def test_create_user_with_company_id__company_member_is_added(self):
        self.authorize(self.superuser)
        # Test response
        payload = self.build_post_data(optional={"role": ADMIN, "company": self.company.id})
        response = self.client.post(self.urls["list"], payload, format="json")
        company_members = self.company.members.values_list("user__username", flat=True)
        self.assertIn(response.data["username"], company_members)

    def test_retrieve(self):
        self.retrieve_request_factory(self.urls["detail_raw"], self.retrieve_cases, lookup_arg="username")

    def test_update(self):
        self.put_request_factory(self.urls["detail_raw"], self.update_cases, lookup_arg="username")

    def test_delete(self):
        self.delete_request_factory(self.urls["detail_raw"], self.delete_cases, lookup_arg="username")

    def test_action_me(self):
        self.get_request_factory(self.urls["me"], self.action_add_me_cases)

    def test_action_me_response(self):
        user = self.force_login()
        response = self.client.get(self.urls["me"])
        response_obj = response.data
        # Test response
        self.assertEqual(len(response_obj), 4)
        self.assertEqual(response_obj["id"], user.id)
        self.assertEqual(response_obj["username"], user.username)
        self.assertEqual(response_obj["role"], user.role)
        self.assertEqual(response_obj["is_active"], user.is_active)

    def test_action_create_info(self):
        self.get_request_factory(self.urls["add"], self.action_add_me_cases)

    def test_action_add_response(self):
        self.authorize(self.superuser)
        # Test response
        response = self.client.get(self.urls["add"])
        response_obj = response.data
        # Test response
        self.assertEqual(len(response_obj), 9)
        self.assertIn("username", response_obj)
        self.assertIn("password", response_obj)
        self.assertIn("first_name", response_obj)
        self.assertIn("middle_name", response_obj)
        self.assertIn("last_name", response_obj)
        self.assertIn("email", response_obj)
        self.assertIn("phone_number", response_obj)
        self.assertIn("username", response_obj)
        self.assertIn("role", response_obj)
        self.assertIn("company", response_obj)
