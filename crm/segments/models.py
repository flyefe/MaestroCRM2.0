from django.db import models
from django.contrib.auth.models import User
from contacts.models import ContactDetail
from settings.models import Status, Tag

class Segment(models.Model):
    LOGIC = [
        ('EQ', '=='),
        ('NOTEQ', '!='),
    ]
    
    LOGICAL_OPERATORS = [
        ('AND', 'AND'),
        ('OR', 'OR'),
    ]

    FIELDS_NAME = [
        ('STATUS', 'status'),
        ('TAGS', 'tags'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    conditions = models.JSONField()  # Store filtering rules in JSON
    contacts = models.ManyToManyField(ContactDetail, blank=True, related_name='segments')
    created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1, related_name='segments_created')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


