from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone  # Import this at the top
from settings.models import Status, Service, TrafficSource, Tag



class ContactDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contact')
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], blank=True)
    marital_status = models.CharField(max_length=20, choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed'), ('Other', 'Other')], blank=True)
    date_of_birth = models.DateTimeField(blank=True, null=True)
    # address = models.OneToOneField('Address', on_delete=models.CASCADE, null=True, blank=True, related_name='contact')

     # Address fields added directly to the ContactDetail model
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    

    services = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, related_name='contacts', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='contacts')
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_contacts')
    traffic_source = models.ForeignKey(TrafficSource, on_delete=models.SET_NULL, null=True, blank=True, related_name='traffic_source_contact')
    new_or_old = models.CharField(max_length=20, choices=[('New', 'New'), ('Old', 'Old')], blank=True) #Can help in scheduling follow-ups or communications.
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='referee_contacts')
   
    preferred_contact_method = models.CharField(max_length=20, choices=[('Email', 'Email'), ('Phone', 'Phone'), ('Text', 'Text'), ('Mail', 'Mail')], blank=True) #Helps in choosing how to best reach the contact.
    contact_frequency = models.CharField(max_length=20, choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('On Demand', 'On Demand')], blank=True) #Can help in scheduling follow-ups or communications.
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contacts')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True) #Can be used to track last contacted
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_contacts')
    close_date = models.DateTimeField(blank=True, null=True)

    custom_field_1 = models.CharField(max_length=255, blank=True, null=True)#Depending on business needs, might have specific data points to track. This could be expanded with more fields or dynamically through a generic foreign key to a custom field model.
    marketing_consent = models.BooleanField(default=False, help_text="Has this contact consented to marketing communications?")
    gdpr_compliant = models.BooleanField(default=False, help_text="Is this contact GDPR compliant?")

    def __str__(self):
        return f"{self.user.username} - {self.status.name if self.status else 'No Status'}"
    


class Log(models.Model):
    LOG_TYPE_CHOICES = [
        # ('call', 'Call'),
        # ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('feedback', 'Feedback'),
    ]
    contact = models.ForeignKey(ContactDetail, related_name='log', on_delete=models.CASCADE)
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES)  # Options filled in
    log_title = models.CharField(max_length=255)  # Added this field
    log_description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='created_log', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Set at creation
    modified_at = models.DateTimeField(auto_now=True)      # Updated on save

    def __str__(self):
        return f'commented by {self.created_by.username} on {self.created_at}'











# class Address(models.Model):
#     """
#     Model representing an address associated with a contact.
    
#     Fields:
#     - first_line: The primary line of the address (e.g., street address)
#     - second_line: An optional second line for additional address details
#     - city: The city or town of the address
#     - state: The state or province (optional for countries without states)
#     - country: The country of the address
#     - postal_code: The postal or zip code
#     """

#     first_line = models.CharField(max_length=255, help_text="Primary address line")
#     second_line = models.CharField(max_length=255, blank=True, help_text="Secondary address line (optional)")
#     city = models.CharField(max_length=100, help_text="City or town")
#     state = models.CharField(max_length=100, blank=True, help_text="State or province (if applicable)")
#     country = models.CharField(max_length=50, help_text="Country")
#     postal_code = models.CharField(max_length=20, help_text="Postal or zip code")

#     def __str__(self):
#         # Return a string representation of the address
#         if self.second_line:
#             return f"{self.first_line}, {self.second_line}, {self.city}, {self.country} - {self.postal_code}"
#         else:
#             return f"{self.first_line}, {self.city}, {self.country} - {self.postal_code}"

#     class Meta:
#         verbose_name_plural = "Addresses"