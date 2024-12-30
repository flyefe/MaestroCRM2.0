from django.db import models
from django.contrib.auth.models import User
from contacts.models import Contact



class SegCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class Segment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    conditions = models.JSONField()  # Store filtering rules in JSON
    contacts = models.ManyToManyField(Contact, blank=True, related_name='segments')
    created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1, related_name='segments_created')
    category = models.ForeignKey(SegCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='segments')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
