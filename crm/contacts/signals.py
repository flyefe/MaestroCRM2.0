from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Contact
from django.contrib.auth.models import User

@receiver(post_save, sender=Contact)
def update_user_from_contact(sender, instance, **kwargs):
    """
    Update the associated User's first_name and last_name whenever the Contact is updated.
    """

    # print(f'contact signal initialized for user account')
    if instance.user:
        user = instance.user
        if user.first_name != instance.first_name or user.last_name != instance.last_name or user.email != instance.email:
            user.first_name = instance.first_name
            user.last_name = instance.last_name
            instance.email = user.email
            user.save()
            # print(f'user updated to {user.first_name} and {user.last_name} and {user.email}')

@receiver(post_save, sender=User)
def update_contact_from_user(sender, instance, **kwargs):
    """
    Update the associated Contact's first_name and last_name whenever the User is updated.
    """

    # print(f'user signal initialized for contact')
    try:
        contact = instance.contact  # Assuming a one-to-one relationship
        if contact.first_name != instance.first_name or contact.last_name != instance.last_name:
            contact.first_name = instance.first_name
            contact.last_name = instance.last_name
            contact.save()
            # print(f'contact names updated to {contact.first_name} and {contact.last_name}')
    except Contact.DoesNotExist:
        # If the user has no associated Contact, skip the update
        pass
