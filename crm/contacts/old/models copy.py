from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone  # Import this at the top
from settings.models import Status, Service, TrafickSource


class ContactDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.CharField(max_length=100, blank=True)  # Comma-separated tags
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_contacts')
    phone_number = models.CharField(max_length=15, blank=True)  # Adjust max_length as needed

    # Address fields directly within ContactDetail
    address_first_line = models.CharField(max_length=255, null=True, blank=True)
    address_second_line = models.CharField(max_length=255, null=True, blank=True)
    address_city = models.CharField(max_length=100, null=True, blank=True)
    address_country = models.CharField(max_length=100, null=True, blank=True)
    address_postal_code = models.CharField(max_length=20, null=True, blank=True)

    trafick_source = models.ForeignKey(TrafickSource, on_delete=models.SET_NULL, null=True, blank=True)
    services = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    open_date = models.DateTimeField(blank=True, null=True)
    close_date = models.DateTimeField(blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contacts')
    created_at = models.DateTimeField(auto_now_add=True)  # Set at creation
    modified_at = models.DateTimeField(auto_now=True)      # Updated on save
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_contacts')
    
    def __str__(self):
        return f"{self.user.username} - {self.status.name if self.status else 'No Status'}"

# Signal to automatically assign the Contact group to the user on creation
@receiver(post_save, sender=ContactDetail)
def assign_contact_group(sender, instance, created, **kwargs):
    if created:
        contact_group, _ = Group.objects.get_or_create(name="Contact")
        instance.user.groups.add(contact_group)


class Log(models.Model):
    LOG_TYPE_CHOICES = [
        ('call', 'Call'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('others', 'Others'),
    ]
    contact = models.ForeignKey(ContactDetail, related_name='log', on_delete=models.CASCADE)
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES)  # Options filled in
    log_title = models.CharField(max_length=255)  # Added this field
    log_description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='client_comment', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Set at creation
    modified_at = models.DateTimeField(auto_now=True)      # Updated on save

    def __str__(self):
        return f'commented by {self.created_by.username} on {self.created_at}'
