from django.db.models import Q
from .models import Segment
from contacts.models import Contact

def reevaluate_segments_for_contacts(contacts_queryset):
    """
    Reevaluate segment conditions for a contacts_queryset of Contact instances.
    Adds matching contacts to the segment and removes non-matching ones
    without affecting unrelated contacts.
    """

    # Ensure contacts is a queryset
    if isinstance(contacts_queryset, Contact):
        contacts_queryset = Contact.objects.filter(pk=contacts_queryset.pk)
    print(f"Reevaluating segments for {contacts_queryset.count()} contacts")

    

    # Loop through all segments
    for segment in Segment.objects.all():
        conditions = segment.conditions
        if not conditions:
            continue  # Skip segments with no conditions

        current_q = None  # Start building the Q query

        # Build dynamic query based on conditions
        for condition in conditions:
            new_q = Q()
            if condition['type'] == 'status':
                if condition['operation'] == '=':
                    new_q &= Q(status=condition['value'])
                elif condition['operation'] == '!=':
                    new_q &= ~Q(status=condition['value'])
            elif condition['type'] == 'tag':
                if condition['operation'] == '=':
                    new_q &= Q(tags=condition['value'])
                elif condition['operation'] == '!=':
                    new_q &= ~Q(tags=condition['value'])

            # Combine logic: 'and' or 'or'
            if current_q is None:
                current_q = new_q
            else:
                if condition.get('logic') == 'and':
                    current_q &= new_q
                elif condition.get('logic') == 'or':
                    current_q |= new_q
       
       
        # Evaluate which contacts match the segment conditions
        matching_contacts = contacts_queryset.filter(current_q)

        print(f"Segment '{segment.name}' matches {matching_contacts.count()} contacts")

        # Add matching contacts that are not already in the segment
        existing_contacts = segment.contacts
        contacts_to_add = matching_contacts.exclude(pk__in=segment.contacts.all())
        if contacts_to_add.exists():
            existing_contacts.add(*contacts_to_add)
            print(f"Added {contacts_to_add.count()} contacts to segment '{segment.name}'")

        # Remove contacts that no longer match the segment conditions
        # contacts_to_remove = existing_contacts.exclude(pk__in=matching_contacts)
        contacts_to_remove = contacts_queryset.filter(pk__in=segment.contacts.all()).exclude(pk__in=matching_contacts)
        if contacts_to_remove.exists():
            segment.contacts.remove(*contacts_to_remove)
            print(f"Removed {contacts_to_remove.count()} contacts from segment '{segment.name}'")