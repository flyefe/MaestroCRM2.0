from django.db.models.signals import post_save
from django.dispatch import receiver
from contacts.models import ContactDetail
from .utils import reevaluate_segments_for_contacts

@receiver(post_save, sender=ContactDetail)
def update_segments_on_contact_save(sender, instance, **kwargs):
    """
    Signal to update segment contacts when a single ContactDetail instance is saved.
    """
    print("Signal triggered: Reevaluating segments for a saved contact")
    # Reevaluate only the saved contact instance
    reevaluate_segments_for_contacts(ContactDetail.objects.filter(pk=instance.pk))
