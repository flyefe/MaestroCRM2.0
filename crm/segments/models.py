# from django.db import models
# from django.contrib.auth.models import User
# from contacts.models import ContactDetail

# class Segment(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     conditions = models.JSONField()  # Store filtering rules in JSON
#     contacts = models.ManyToManyField(ContactDetail, blank=True, related_name='segments')
#     created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1, related_name='segments_created')
#     created_at = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)


from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from contacts.models import ContactDetail
import json

class Segment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    conditions = models.JSONField()  # Store filtering rules in JSON
    created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1, related_name='segments_created')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_matching_contacts(self):
        """
        Dynamically filter and return contacts matching the segment's conditions.
        """
        if not self.conditions:
            return ContactDetail.objects.none()  # Return an empty queryset if no conditions exist
        
        current_q = None

        # Build the dynamic Q query based on conditions
        for condition in self.conditions:
            new_q = Q()
            if condition['type'] == 'status':
                if condition['operation'] == '=':
                    new_q &= Q(status=condition['value'])
                elif condition['operation'] == '!=':
                    new_q &= ~Q(status=condition['value'])
            elif condition['type'] == 'tag':
                if condition['operation'] == '=':
                    new_q &= Q(tags__name=condition['value'])
                elif condition['operation'] == '!=':
                    new_q &= ~Q(tags__name=condition['value'])

            # Combine conditions using AND/OR logic
            if current_q is None:
                current_q = new_q
            else:
                if condition.get('logic') == 'and':
                    current_q &= new_q
                elif condition.get('logic') == 'or':
                    current_q |= new_q

        # Return filtered contacts
        return ContactDetail.objects.filter(current_q) if current_q else ContactDetail.objects.none()
