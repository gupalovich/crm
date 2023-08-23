from django.test import RequestFactory, TestCase
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.test import APIRequestFactory

from crm.companies.tests.factories import (
    CompanyFactory,
    CompanyMemberFactory,
    CompanyProductLinkFactory,
    CompanyTypeFactory,
    CustomerFactory,
    ProductFactory,
)
from crm.users.tests.factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory

from ..permissions import (
    CanModifyUserPermission,
    IsAdminPermission,
    IsManagerPermission,
    IsSuperPermission,
    validate_company_product_link,
    validate_customer_company_membership,
    validate_product,
    validate_user_company_membership,
    validate_user_company_type,
)


class ValidateProduct(TestCase):
    def setUp(self):
        self.product = ProductFactory(is_active=True)

    def test_valid(self):
        validate_product(self.product)

    def test_invalid(self):
        self.product.is_active = False
        with self.assertRaises(PermissionDenied) as context:
            validate_product(self.product)
        self.assertIn(f"Товар: [{self.product.name}] неактивен", str(context.exception))


class ValidateCompanyProductLink(TestCase):
    def setUp(self):
        self.company_product_link = CompanyProductLinkFactory(is_valid=True)

    def test_valid(self):
        validate_company_product_link(self.company_product_link)

    def test_invalid(self):
        self.company_product_link.is_valid = False
        with self.assertRaises(ValidationError) as context:
            validate_company_product_link(self.company_product_link)
        self.assertIn("Неверная ссылка", str(context.exception))


class ValidateUserCompanyType(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = SuperUserFactory()
        self.company_type = CompanyTypeFactory(user=self.superuser)
        self.other_company_type = CompanyTypeFactory()

    def test_valid(self):
        request = self.factory.get("/")
        request.user = self.superuser
        validate_user_company_type(request, self.company_type)

    def test_invalid(self):
        request = self.factory.get("/")
        request.user = self.superuser
        with self.assertRaises(PermissionDenied):
            validate_user_company_type(request, self.other_company_type)


class ValidateCustomerCompanyMembership(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = SuperUserFactory()
        # create companies
        self.company = CompanyFactory()
        self.company_member = CompanyMemberFactory(user=self.superuser, company=self.company)
        # create customers
        self.customer = CustomerFactory(company=self.company)
        self.other_customer = CustomerFactory()
        # build request
        self.request = self.factory.get("/")
        self.request.user = self.superuser

    def test_valid(self):
        validate_customer_company_membership(self.request, self.customer)

    def test_invalid(self):
        with self.assertRaises(PermissionDenied):
            validate_customer_company_membership(self.request, self.other_customer)


class ValidateUserCompanyMembership(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = SuperUserFactory()
        self.other_superuser = SuperUserFactory()
        self.company = CompanyFactory()
        self.company_member = CompanyMemberFactory(user=self.superuser, company=self.company)

    def test_user_with_membership_should_pass_validation(self):
        request = self.factory.get("/")
        request.user = self.superuser
        # Pass the user and a company associated with the user's membership
        validate_user_company_membership(request, self.company)

    def test_user_without_membership_should_raise_permission_denied(self):
        request = self.factory.get("/")
        request.user = self.other_superuser
        # Pass the user and a company associated with a different user's membership
        with self.assertRaises(PermissionDenied):
            validate_user_company_membership(request, self.company)

    def test_company_is_none_should_pass_validation(self):
        request = self.factory.get("/")
        request.user = self.superuser
        # Pass the user and a None company (not associated with any membership)
        validate_user_company_membership(request, None)


class CanModifyUserPermissionTests(TestCase):
    def setUp(self):
        self.permission = CanModifyUserPermission()
        self.rf = APIRequestFactory()
        # create users
        self.superuser = SuperUserFactory()
        self.admin = AdminUserFactory()
        self.manager = ManagerUserFactory()
        # create test cases
        self.permission_cases = [  # requested, to_modify, expected_result
            (self.superuser, self.admin, True, "SUPERUSER can modify ADMIN"),
            (self.superuser, self.superuser, True, "SUPERUSER can modify SUPERUSER"),
            (self.admin, self.superuser, False, "ADMIN can't modify SUPERUSER"),
            (self.admin, self.admin, True, "ADMIN can modify ADMIN"),
        ]

    def test_permissions(self):
        for requested, to_modify, expected_result, *optional_args in self.permission_cases:
            request = self.rf.post("/")
            request.user = requested
            is_permitted = self.permission.has_object_permission(request, None, to_modify)
            self.assertEqual(is_permitted, expected_result, *optional_args)

    def test_admin_cant_delete_self(self):
        request = self.rf.post("/")
        request.user = self.admin
        request.method = "DELETE"
        is_permitted = self.permission.has_object_permission(request, None, self.admin)
        self.assertEqual(is_permitted, False, "ADMIN can't delete himself")


class IsSuperPermissionTests(TestCase):
    def setUp(self):
        self.super_cases = [
            (SuperUserFactory(), True),
            (SuperUserFactory(is_active=False), False),
        ]
        self.admin_cases = [
            (AdminUserFactory(), False),
            (AdminUserFactory(is_active=False), False),
        ]
        self.manager_cases = [
            (ManagerUserFactory(), False),
            (ManagerUserFactory(is_active=False), False),
        ]
        self.permission = IsSuperPermission()
        self.rf = APIRequestFactory()

    def test_with_superuser(self):
        for user, expected_result in self.super_cases:
            request = self.rf.get("/")
            request.user = user
            self.assertEqual(self.permission.has_permission(request, None), expected_result)

    def test_with_admin(self):
        for user, expected_result in self.admin_cases:
            request = self.rf.get("/")
            request.user = user
            self.assertEqual(self.permission.has_permission(request, None), expected_result)

    def test_with_manager(self):
        for user, expected_result in self.manager_cases:
            request = self.rf.get("/")
            request.user = user
            self.assertEqual(self.permission.has_permission(request, None), expected_result)


class IsAdminPermissionTests(TestCase):
    def setUp(self):
        self.super_cases = [
            (SuperUserFactory(), False),
            (SuperUserFactory(is_active=False), False),
        ]
        self.admin_cases = [
            (AdminUserFactory(), True),
            (AdminUserFactory(is_active=False), False),
        ]
        self.manager_cases = [
            (ManagerUserFactory(), False),
            (ManagerUserFactory(is_active=False), False),
        ]
        self.permission = IsAdminPermission()
        self.rf = APIRequestFactory()

    def test_with_superuser(self):
        for user, expected_result in self.super_cases:
            request = self.rf.get("/")
            request.user = user
            self.assertEqual(self.permission.has_permission(request, None), expected_result)

    def test_with_admin(self):
        for user, expected_result in self.admin_cases:
            request = self.rf.get("/")
            request.user = user
            self.assertEqual(self.permission.has_permission(request, None), expected_result)

    def test_with_manager(self):
        for user, expected_result in self.manager_cases:
            request = self.rf.get("/")
            request.user = user
            self.assertEqual(self.permission.has_permission(request, None), expected_result)


class IsManagerPermissionTests(TestCase):
    def setUp(self):
        self.super_cases = [
            (SuperUserFactory(), False),
            (SuperUserFactory(is_active=False), False),
        ]
        self.admin_cases = [
            (AdminUserFactory(), False),
            (AdminUserFactory(is_active=False), False),
        ]
        self.manager_cases = [
            (ManagerUserFactory(), True),
            (ManagerUserFactory(is_active=False), False),
        ]
        self.permission = IsManagerPermission()
        self.rf = APIRequestFactory()

    def test_with_superuser(self):
        for user, expected_result in self.super_cases:
            request = self.rf.get("/")
            request.user = user
            self.assertEqual(self.permission.has_permission(request, None), expected_result)

    def test_with_admin(self):
        for user, expected_result in self.admin_cases:
            request = self.rf.get("/")
            request.user = user
            self.assertEqual(self.permission.has_permission(request, None), expected_result)

    def test_with_manager(self):
        for user, expected_result in self.manager_cases:
            request = self.rf.get("/")
            request.user = user
            self.assertEqual(self.permission.has_permission(request, None), expected_result)
