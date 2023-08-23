import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase

from .factories import AdminUserFactory, ManagerUserFactory, SuperUserFactory, UserFactory

User = get_user_model()


class UserGroupAssignmentSignalTests(TestCase):
    def setUp(self):
        call_command("create_groups")
        # get groups
        self.superuser_group = Group.objects.get(name="Superuser")
        self.admin_group = Group.objects.get(name="Admin")
        self.manager_group = Group.objects.get(name="Manager")
        # create users
        self.superuser = SuperUserFactory()
        self.admin = AdminUserFactory()
        self.manager = ManagerUserFactory()

    def test_user_group_manager_signal_for_superuser(self):
        # Check that the user is added to superuser group
        self.assertIn(self.superuser_group, self.superuser.groups.all())
        self.assertNotIn(self.admin_group, self.superuser.groups.all())
        self.assertNotIn(self.manager_group, self.superuser.groups.all())

    def test_user_group_manager_signal_for_admin(self):
        # Check that the user is added to admin group
        self.assertNotIn(self.superuser_group, self.admin.groups.all())
        self.assertIn(self.admin_group, self.admin.groups.all())
        self.assertNotIn(self.manager_group, self.admin.groups.all())

    def test_user_group_manager_signal_for_manager(self):
        # Check that the user is added to manager group
        self.assertNotIn(self.superuser_group, self.manager.groups.all())
        self.assertNotIn(self.admin_group, self.manager.groups.all())
        self.assertIn(self.manager_group, self.manager.groups.all())


@pytest.mark.django_db(transaction=True)
def test_user_role_change_changes_group():
    call_command("create_groups")

    user = UserFactory()
    roles_to_test = [
        User.Roles.ADMIN,
        User.Roles.MANAGER,
        User.Roles.SUPERUSER,
    ]

    for role in roles_to_test:
        # Update the role
        user.role = role
        user.save()
        # Test group changed to the corresponding role
        assert user.groups.count() == 1
        assert user.groups.first().name == role.capitalize()
    # Test groups was not duplicated
    assert Group.objects.count() == len(roles_to_test)
