from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase

User = get_user_model()


class CreateGroupsCommandTestCase(TestCase):
    def test_create_user_groups(self):
        call_command("create_groups")

        superuser_group = Group.objects.get(name="Superuser")
        admin_group = Group.objects.get(name="Admin")
        manager_group = Group.objects.get(name="Manager")

        self.assertEqual(superuser_group.permissions.count(), 33)
        self.assertEqual(admin_group.permissions.count(), 19)
        self.assertEqual(manager_group.permissions.count(), 5)
