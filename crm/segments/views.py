import json, random, string
from django.db.models import Q
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Segment
from .forms import SegmentForm

from contacts.models import ContactDetail
from contacts.forms import ContactDetailCreationForm, ContactFilterForm, ContactSearchForm

from core.decorators import role_required

@role_required(['Admin'])
@login_required
def delete_segment(request, pk):
    #Get thesegment to be deleted form the database
    segment = get_object_or_404(Segment, pk=pk)

    segment.delete()
    messages.success(request, f" Segment has been successfully deleted.")
    return redirect('segments:list')

@login_required
def bulk_action(request):
    if request.method == "POST":
        action_type = request.POST.get("action_type")
        selected_segments = request.POST.get("selected_segments", "").split(',')

        print(action_type)
        
        # Ensure segments are selected
        if not selected_segments:
            messages.error(request, "No segments selected.")
            return redirect("segments:list")       
        
        # Handle each action       
        if action_type == "delete":
            segments=Segment.objects.filter(id__in=selected_segments)

            for segment in segments:
                segment.delete() #Delete the Segment Object
            messages.success(request, "Selected segments deleted successfully!")
        
        else:
            messages.error(request, "Invalid action selected.")
        
        return redirect("segments:list")
    return redirect('segments:list')

@role_required(['Admin'])
def edit_segment(request, pk):
    # Get the segment object from the database
    segment = get_object_or_404(Segment, pk=pk)

    # Retrieve the conditions (assuming it's a JSON field in the model)
    existing_conditions = segment.conditions  # Assuming `conditions` is a JSON field in your model
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        conditions = json.loads(request.POST.get('conditions', '[]'))
        print(conditions)

        # Initialize the main Q object for filtering contacts
        q = Q()
        current_q = None  # Variable to keep track of the current condition

        for i, condition in enumerate(conditions):
            # Create a new Q object for each condition
            new_q = Q()

            # Handle the condition based on type and operation
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

            # Logic for combining conditions (AND/OR)
            if i == 0:
                current_q = new_q
            else:
                if condition['logic'] == 'and':
                    current_q &= new_q
                elif condition['logic'] == 'or':
                    current_q |= new_q

        # After the loop, current_q holds the combined query
        if current_q:
            q = current_q

        # Filter contacts based on the Q object
        filtered_contacts = ContactDetail.objects.filter(q)

        # Update the segment with the new data
        segment.name = name
        segment.description = description
        segment.conditions = conditions  # Save the updated conditions
        segment.modified_at = now()  # Update the modification timestamp
        segment.save()  # Save the changes

        # Optional: Save filtered contacts to the segment if needed
        segment.contacts.clear()  # Clear existing contacts first
        for contact in filtered_contacts:
            segment.contacts.add(contact)  # Assuming you have a ManyToMany relationship with contacts

        messages.success(request, "Segment updated successfully!")
        return redirect('segments:list')  # Redirect to the segment list or another appropriate page

    else:
        # Handle GET request and pass initial data to the form
        form = SegmentForm(instance=segment)

        # Pass the existing conditions to the form as a JSON string for the front end
        if existing_conditions:
            form.fields['conditions'].initial = json.dumps(existing_conditions)

    context = {
        'form': form,
        'existing_conditions': json.dumps(existing_conditions),  # Pass the conditions as JSON to the template
    }

    return render(request, 'segments/edit_segment.html', context)

@role_required(['Admin'])
@login_required
def add_segment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        conditions = json.loads(request.POST.get('conditions', '[]'))
        print(conditions)

        # Initialize the main Q object
        q = Q()

        # Variable to keep track of the current condition
        current_q = None

        for i, condition in enumerate(conditions):
            # Create a new Q object for each condition
            new_q = Q()

            # Apply the condition based on type and operation
            if condition['type'] == 'status':
                if condition['operation'] == '=':
                    new_q = Q(status__id=condition['value'])
                elif condition['operation'] == '!=':
                    new_q = ~Q(status__id=condition['value'])
            elif condition['type'] == 'tag':
                if condition['operation'] == '=':
                    new_q = Q(tags__id=condition['value'])
                elif condition['operation'] == '!=':
                    new_q = ~Q(tags__id=condition['value'])

            # Combine conditions
            if i == 0:
                # For the first condition, directly set `current_q`
                current_q = new_q
            else:
                # Combine with the previous condition based on the logic
                if condition['logic'] == 'and':
                    current_q &= new_q
                elif condition['logic'] == 'or':
                    current_q |= new_q

        # After the loop, assign `current_q` to `q`
        if current_q:
            q = current_q

        # Filter contacts based on the Q object
        filtered_contacts = ContactDetail.objects.filter(q)

        # Save the segment
        segment = Segment.objects.create(
            name=name,
            description=description,
            created_by=request.user,  # Assuming you have a `created_by` field in the Segment model
            created_at=now(),
            modified_at=now(),
            conditions=conditions,
        )

        # Optional: Save filtered contacts to the segment if needed
        for contact in filtered_contacts:
            segment.contacts.add(contact)  # Assuming you have a ManyToMany relationship with contacts

        return redirect('segments:list')  # Redirect to a segment list page or detail view after saving
    else:
        form = SegmentForm()

    context = {
        'form': form
    }

    return render(request, 'segments/create_segment.html', context)

@login_required
def segment_list(request):
    segments = Segment.objects.all().order_by('-created_by')

    # Add pagination (Optional)
    paginator = Paginator(segments, 10)  # Show 10 contacts per page
    page_number = request.GET.get('page')
    page_segments = paginator.get_page(page_number)
    
    return render(request, 'segments/segment_list.html', {'segments': page_segments})

@login_required
def segment_contacts(request, pk):
    segment = get_object_or_404(Segment, pk=pk)
    # contacts = segment.get_contacts()
    contacts = segment.contacts.all()

    # Add pagination (Optional)
    paginator = Paginator(contacts, 10)  # Show 10 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)

    form = ContactDetailCreationForm
    filter_form = ContactFilterForm
    search_form = ContactSearchForm

    context = {
        'segment': segment,
        'contacts': page_contacts,
        'form': form,
        'filter_form': filter_form,
        'search_form' : search_form
    }
    return render(request,'segments/segment_contacts.html', context)
