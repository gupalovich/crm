from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory, UserFactory

User = get_user_model()


class UserTests(TestCase):
    def setUp(self):
        self.batch_size = 3
        self.test_name = "Иван"
        self.user = UserFactory()
        self.init_user_count = User.objects.count()

    def test_create(self):
        UserFactory.create_batch(self.batch_size)
        self.assertEqual(User.objects.count(), self.batch_size + self.init_user_count)

    def test_update(self):
        self.user.first_name = self.test_name
        self.user.full_clean()
        self.user.save()
        self.assertEqual(self.user.first_name, self.test_name)

    def test_delete(self):
        self.user.delete()
        self.assertEqual(User.objects.count(), 0)

    def test_fields(self):
        self.assertTrue(self.user.memberships)
        self.assertTrue(self.user.username)
        self.assertTrue(self.user.first_name)
        self.assertTrue(self.user.middle_name)
        self.assertTrue(self.user.last_name)
        self.assertTrue(self.user.email)
        self.assertTrue(self.user.phone_number)
        self.assertTrue(self.user.tracker)

    def test_phone_number_required(self):
        with self.assertRaises(ValidationError):
            self.user.phone_number = ""
            self.user.full_clean()
            self.user.save()

    def test_email_not_required(self):
        self.user.email = ""
        self.user.full_clean()
        self.user.save()

    def test_str(self):
        self.assertEqual(self.user.username, str(self.user))

    def test_property_is_crm_superuser(self):
        user = SuperUserFactory()
        self.assertTrue(user.is_crm_superuser)
        self.assertFalse(user.is_crm_admin)
        self.assertFalse(user.is_crm_manager)

    def test_property_is_crm_admin(self):
        user = AdminUserFactory()
        self.assertFalse(user.is_crm_superuser)
        self.assertTrue(user.is_crm_admin)
        self.assertFalse(user.is_crm_manager)

    def test_property_is_crm_manager(self):
        user = ManagerUserFactory()
        self.assertFalse(user.is_crm_superuser)
        self.assertFalse(user.is_crm_admin)
        self.assertTrue(user.is_crm_manager)
