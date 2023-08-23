from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def user_group_manager_signal(sender, instance, created, **kwargs):
    if created:
        try:
            group = Group.objects.get(name=instance.role.capitalize())
            instance.groups.add(group)
        except Group.DoesNotExist:
            # silent handling to prevent errors in tests and repeating "create_groups"
            pass
    else:
        if instance.role == instance.tracker.previous("role"):
            return
        try:
            new_group = Group.objects.get(name=instance.role.capitalize())
        except Group.DoesNotExist as e:
            raise e
        else:
            transaction.on_commit(lambda: instance.groups.clear())
            transaction.on_commit(lambda: instance.groups.add(new_group))
