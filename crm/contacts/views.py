# import re
from django.db.models.functions import Coalesce
from django.db.models import Q, Subquery, OuterRef, CharField, Value
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth.hashers import make_password
import random, string
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User, Group
from .forms import ContactDetailCreationForm, LogForm, ContactFilterForm, ContactSearchForm
from .models import ContactDetail, Log
# from .utility import filter_contacts
from settings.models import Tag, Status, TrafficSource, Service
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.paginator import Paginator


@login_required
def contacts_by_service(request, service_id):
    # Get the service by ID
    service = get_object_or_404(Service, id=service_id)
    
    # Filter contacts by status
    contacts = ContactDetail.objects.filter(services=service)
    
    # Add pagination (Optional)
    paginator = Paginator(contacts, 2)  # Show 10 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)
    
    # Render the filtered contacts
    return render(request, 'contact/contacts_by_filter.html', {
        'service': service,
        'contacts': page_contacts,  # Pass paginated contacts if using pagination
    })


@login_required
def contacts_by_traffic_source(request, traffic_source_id):
    # Get the traffic_source ID
    traffic_source = get_object_or_404(TrafficSource, id=traffic_source_id)
    
    # Filter contacts by traffic_source
    contacts = ContactDetail.objects.filter(traffic_source=traffic_source)
    
    # Add pagination (Optional)
    paginator = Paginator(contacts, 2)  # Show 10 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)
    
    # Render the filtered contacts
    return render(request, 'contact/contacts_by_filter.html', {
        'traffic_source': traffic_source,
        'contacts': page_contacts,  # Pass paginated contacts if using pagination
    })

@login_required
def contacts_by_assigned_staff(request, assigned_staff_id):
    # Get the staff by ID
    assigned_staff = get_object_or_404(User, id=assigned_staff_id)
    
    # Filter contacts by staff
    contacts = ContactDetail.objects.filter(assigned_staff=assigned_staff)
    
    # Add pagination (Optional)
    paginator = Paginator(contacts, 2)  # Show 10 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)
    
    # Render the filtered contacts
    return render(request, 'contact/contacts_by_filter.html', {
        'assigned_staff': assigned_staff,
        'contacts': page_contacts,  # Pass paginated contacts if using pagination
    })

@login_required
def contacts_by_status(request, status_id):
    # Get the status by ID
    status = get_object_or_404(Status, id=status_id)
    
    # Filter contacts by status
    contacts = ContactDetail.objects.filter(status=status)
    
    # Add pagination (Optional)
    paginator = Paginator(contacts, 2)  # Show 10 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)
    
    # Render the filtered contacts
    return render(request, 'contact/contacts_by_filter.html', {
        'status': status,
        'contacts': page_contacts,  # Pass paginated contacts if using pagination
    })

@login_required
def contacts_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)  # Get the tag by ID
    contacts = ContactDetail.objects.filter(tags=tag)  # Filter contacts by tag

     # Add pagination (Optional)
    paginator = Paginator(contacts, 2)  # Show 10 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)

    return render(request, 'contact/contacts_by_filter.html', {
        'tag': tag,
        'contacts': page_contacts
    })

@login_required
def delete_log(request, log_id):

    log = get_object_or_404(Log, id=log_id)

    log.delete()

    contact_id = log.contact_id
    
    messages.success(request, f" Log has been successfully deleted.")
    return redirect ('contact_detail', contact_id)

@login_required
def update_log(request, log_id):
    log = get_object_or_404(Log, id=log_id)
    contact_id = log.contact_id

    if request.method == 'POST':
        form = LogForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            messages.success(request, "Log updated successfully.")
            return redirect('contact_detail', contact_id=contact_id)
    else:
        # Populate form with current log details
        form = LogForm(instance=log)

    context = {
        'contact_id': contact_id,
        'form': form,
        'log_id': log_id
    }

    return render(request, 'contact/update_log.html', context)

@login_required
def contact_detail(request, contact_id, log_id=None):
    contact = get_object_or_404(ContactDetail, id=contact_id)

    # Fetch recent activities (assuming Log model has a ForeignKey to ContactDetail)
    recent_activities = contact.log.all().order_by('-created_at')[:3]
    logs = Log.objects.filter(contact=contact).order_by('-created_at')

    # If log_id is provided, get the specific log and populate the form for editing
    form = LogForm()
    if log_id:
        log = get_object_or_404(Log, id=log_id)
        form = LogForm(instance=log)  # Populate the form with the current log details

    # Handle form submission for new logs
    if request.method == 'POST' and not log_id:
        form = LogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.contact = contact
            log.created_by = request.user
            log.save()
            messages.success(request, "Log added successfully.")
            return redirect('contact_detail', contact_id=contact_id)
    elif request.method == 'POST' and log_id:
        # Update the existing log
        form = LogForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            messages.success(request, "Log updated successfully.")
            return redirect('contact_detail', contact_id=contact_id)

    context = {
        'contact': contact,
        'recent_activities': recent_activities,
        'logs': logs,
        'form': form,
        'log_id': log_id,  # Pass the log_id to identify the form in the template
    }
    return render(request, 'contact/contact_detail.html', context)

@login_required
def delete_contact(request, contact_id):
    # Check if the user has permission to delete a user (since deleting a contact also deletes the user)
    if not request.user.has_perm('auth.delete_user'):
        messages.error(request, "You do not have permission to delete contacts or associated user accounts.")
        return redirect('contact_list')  # Assuming you have a contact list view

    contact = get_object_or_404(ContactDetail, id=contact_id)
    
    # Check if the user is trying to delete their own contact
    if contact.user == request.user:
        messages.error(request, "You cannot delete your own contact.")
        return redirect('contact_detail', contact_id=contact.id)

    # Delete the contact first
    contact.delete()

    # Then delete the associated user
    user = contact.user
    user.delete()

    messages.success(request, f"Contact '{contact.user.first_name}' and associated user account have been successfully deleted.")
    return redirect('contact_list')  # Redirect to contact list or another appropriate page
    
# @login_required
# def contact_list(request):
#     contacts = ContactDetail.objects.select_related('user').all().order_by('-modified_at')  # Retrieves Profile and related User data in a single query
#     # logs = Log.objects.filter(contact=contact).order_by('-created_at')

  
#     # Add pagination (Optional)
#     paginator = Paginator(contacts, 100)  # Show 10 contacts per page
#     page_number = request.GET.get('page')
#     page_contacts = paginator.get_page(page_number)

#     form = ContactDetailCreationForm
#     filter_form = ContactFilterForm
#     search_form = ContactSearchForm


#     context = {
#         'contacts': page_contacts, 
#         'form': form,
#         'filter_form': filter_form,
#         'search_form': search_form,
#         # 'logs': logs
#     }
#     return render(request, 'contact/contact_list.html', context)



@login_required
def my_assigned_contacts(request):
    # Subquery to get the most recent log (type = 'feedback') title
    recent_feedback_log_title = Log.objects.filter(
        contact=OuterRef('pk'),  # Match the Log with the ContactDetail
        log_type='feedback'      # Filter only feedback logs
    ).order_by('-created_at').values('log_title')[:1]  # Get the most recent log title
    
    # Subquery to get the most recent log (type = 'feedback') description
    recent_feedback_log_description = Log.objects.filter(
        contact=OuterRef('pk'),
        log_type='feedback'
    ).order_by('-created_at').values('log_description')[:1]  # Get the most recent log description

    # Add annotations for recent log title and description to ContactDetail
    contacts = ContactDetail.objects.select_related('user').filter(
        assigned_staff= request.user
    ).annotate(
        recent_feedback_log_title=Coalesce(Subquery(recent_feedback_log_title, output_field=CharField()), Value('No Feedback')),
        recent_feedback_log_description=Coalesce(Subquery(recent_feedback_log_description, output_field=CharField()), Value('No Description'))
    ).order_by('-modified_at')

    # Pagination
    paginator = Paginator(contacts, 10)  # Show 10 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)

    # Forms
    form = ContactDetailCreationForm()
    filter_form = ContactFilterForm()
    search_form = ContactSearchForm()

    context = {
        'contacts': page_contacts,
        'form': form,
        'filter_form': filter_form,
        'search_form': search_form,
    }
    return render(request, 'contact/contact_list.html', context)

@login_required
def contact_list(request):
    # Subquery to get the most recent log (type = 'feedback') title
    recent_feedback_log_title = Log.objects.filter(
        contact=OuterRef('pk'),  # Match the Log with the ContactDetail
        log_type='feedback'      # Filter only feedback logs
    ).order_by('-created_at').values('log_title')[:1]  # Get the most recent log title
    
    # Subquery to get the most recent log (type = 'feedback') description
    recent_feedback_log_description = Log.objects.filter(
        contact=OuterRef('pk'),
        log_type='feedback'
    ).order_by('-created_at').values('log_description')[:1]  # Get the most recent log description

    # Add annotations for recent log title and description to ContactDetail
    contacts = ContactDetail.objects.select_related('user').annotate(
        recent_feedback_log_title=Coalesce(Subquery(recent_feedback_log_title, output_field=CharField()), Value('No Feedback')),
        recent_feedback_log_description=Coalesce(Subquery(recent_feedback_log_description, output_field=CharField()), Value('No Description'))
    ).order_by('-modified_at')

    # Pagination
    paginator = Paginator(contacts, 10)  # Show 10 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)

    # Forms
    form = ContactDetailCreationForm()
    filter_form = ContactFilterForm()
    search_form = ContactSearchForm()

    context = {
        'contacts': page_contacts,
        'form': form,
        'filter_form': filter_form,
        'search_form': search_form,
    }
    return render(request, 'contact/contact_list.html', context)


@login_required
def search_contact(request):
    contacts = ContactDetail.objects.select_related('user').all()
    form = ContactDetailCreationForm
    filter_form = ContactFilterForm(request.GET)
    search_form = ContactSearchForm(request.GET or None)
    query = request.GET.get('query', '').strip()
    # contacts = ContactDetail.objects.all()



    if query:
        # Search across multiple fields
        contacts = contacts.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(status__name__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(services__name__icontains=query) |
            Q(traffic_source__name__icontains=query)
        ).distinct()

    # Pagination
    paginator = Paginator(contacts, 5)  # Show 5 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)

    context = {
        'search_form': search_form,
        'form': form,
        'contacts': page_contacts,  # Paginated results
        'query': query,
        'filter_form' : filter_form
    }

    return render(request, 'contact/contact_list.html', context)

@login_required
def filter_contact(request):
    # Initialize form with GET data if available
    filter_form = ContactFilterForm(request.GET)

    #Pass in search form as well
    search_form = ContactSearchForm(request.GET or None)

    form = ContactDetailCreationForm



    # Start with all contacts, then apply filters
    contacts = ContactDetail.objects.select_related('user').all()


    if filter_form.is_valid():
        # Apply filters based on the form data
        if filter_form.cleaned_data['status']:
            contacts = contacts.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data['tags']:
            contacts = contacts.filter(tags=filter_form.cleaned_data['tags'])
        if filter_form.cleaned_data['services']:
            contacts = contacts.filter(services=filter_form.cleaned_data['services'])
        if filter_form.cleaned_data['traffic_source']:
            contacts = contacts.filter(traffic_source=filter_form.cleaned_data['traffic_source'])
        if filter_form.cleaned_data['assigned_staff']:
            contacts = contacts.filter(assigned_staff=filter_form.cleaned_data['assigned_staff'])

    # Pagination
    paginator = Paginator(contacts, 5)  # Show 5 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)

    context = {
        'contacts': page_contacts,
        'form': form,
        'filter_form': filter_form,
        'search_form' : search_form
    }

    return render(request, 'contact/contact_list.html', context)

@login_required
def contacts_bulk_action(request):
    if request.method == "POST":
        action_type = request.POST.get("action_type")
        selected_contacts = request.POST.get("selected_contacts", "").split(',')
        
        # Ensure contacts are selected
        if not selected_contacts:
            messages.error(request, "No contacts selected.")
            return redirect("contact_list")
        
        # Handle each action
        if action_type == "update_status":
            status_id = request.POST.get("status")
            if status_id:
                ContactDetail.objects.filter(id__in=selected_contacts).update(status_id=status_id)
                messages.success(request, "Status updated successfully!")
            else:
                messages.error(request, "No status selected.")
        
        elif action_type == "add_tags":
            # tags_input = request.POST.get("tags", "").split(",")
            tag_ids = request.POST.getlist("tags")
            if tag_ids:
                for contact in ContactDetail.objects.filter(id__in=selected_contacts):                    
                    # Add selected tags
                    contact.tags.add(*tag_ids)
                messages.success(request, "Tags added successfully!")
            else:
                messages.error(request, "No tags provided or selected.")
        
        elif action_type == "remove_tags":
            tag_ids = request.POST.getlist("tags")
            if tag_ids:
                tags = Tag.objects.filter(id__in=tag_ids)
                contacts = ContactDetail.objects.filter(id__in=selected_contacts)

                for contact in contacts:
                    # Remove selected tags
                    contact.tags.remove(*tags)
                messages.success(request, "Tags removed successfully!")
            else:
                messages.error(request, "No tags provided or selected.")
        
        elif action_type == "delete":
            contacts=ContactDetail.objects.filter(id__in=selected_contacts)

            for contact in contacts:
                # Delete associated user account if it exists
                if contact.user: #Assuming ContactDetails has relationship with User
                    contact.user.delete()
                contact.delete() #Delete the ContactDetail Object
            messages.success(request, "Selected contacts deleted successfully!")

        elif action_type == "assign_staff":
            assigned_staff_id = request.POST.get("assigned_staff")
            if assigned_staff_id:
                ContactDetail.objects.filter(id__in=selected_contacts).update(assigned_staff_id=assigned_staff_id)                  
                messages.success(request, "Contacts assigned to staff successfully!")
            else:
                messages.error(request, "No staff provided or selected.")

        elif action_type == "traffic_source":
            traffic_source_id = request.POST.get("traffic_source")
            if traffic_source_id:
                ContactDetail.objects.filter(id__in=selected_contacts).update(traffic_source_id=traffic_source_id)                  
                messages.success(request, "Contacts traffic sources updated successfully!")
            else:
                messages.error(request, "No staff provided or selected.")

        elif action_type == "services":
            services_id = request.POST.get("services")
            if services_id:
                ContactDetail.objects.filter(id__in=selected_contacts).update(services_id=services_id)                  
                messages.success(request, "Contacts services updated successfully!")
            else:
                messages.error(request, "No staff provided or selected.")
        
        else:
            messages.error(request, "Invalid action selected.")
        
        return redirect("contact_list")
    return redirect('contact_list')

@login_required
def update_contact(request, contact_id):
    contact = get_object_or_404(ContactDetail, id=contact_id)
    user = contact.user

    if request.method == 'POST':
        form = ContactDetailCreationForm(request.POST, instance=contact)
        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            # tags = [tag.strip().title() for tag in form.cleaned_data['tags'].split(',') if tag.strip()]

             # Extract and merge tags from both fields
            tags_from_text = [tag.strip().title() for tag in form.cleaned_data['tag'].split(',') if tag.strip()]
            tags_from_select = [tag.name.strip() for tag in form.cleaned_data['tags']]  # Taking `tags` is a multi-select field
            combined_tags = set(tags_from_text + tags_from_select)  # Remove duplicates

            # Check if the email has been changed
            if email != user.email:
                # Check if the new email already exists for another user
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    messages.error(request, 'This email is already in use by another contact.')
                    return render(request, 'contact/update_contact_detail.html', {'form': form})
            
            # Update user details
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Update contact details
            contact = form.save(commit=False)
            contact.updated_by = request.user

            # Update tags
            contact.tags.clear()  # Clear existing tags
            for tag_name in combined_tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)  # Create tag if not exists
                contact.tags.add(tag)  # Add tag to contact
                
            contact.save()

            

            messages.success(request, 'Contact and user details updated successfully.')
            return redirect(reverse('contact_detail', args=[contact.id]))
    else:
        # Populate the form with current contact details
        form = ContactDetailCreationForm(instance=contact, initial={
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'tag': ', '.join(contact.tags.values_list('name', flat=True))  # Populate tags as a comma-separated string
        })
        
    return render(request, 'contact/update_contact_detail.html', {'form': form})

@login_required
@transaction.atomic
def create_contact(request):
    if request.method == 'POST':
        form = ContactDetailCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # tags = [tag.strip().title() for tag in form.cleaned_data['tags'].split(',') if tag.strip()]

             # Extract and merge tags from both fields
            tags_from_text = [tag.strip().title() for tag in form.cleaned_data['tag'].split(',') if tag.strip()]
            tags_from_select = [tag.name.strip() for tag in form.cleaned_data['tags']]  # Taking `tags` is a multi-select field
            combined_tags = set(tags_from_text + tags_from_select)  # Remove duplicates

            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

            try:
                # Attempt to get or create the user, which inherently checks for existence
                user, created = User.objects.get_or_create(
                    username=email,
                    defaults={
                        'email': email,
                        'first_name': form.cleaned_data['first_name'],
                        'last_name': form.cleaned_data['last_name'],
                    }
                )
                
                if not created:
                    messages.error(request, "A user with this email already exists.")
                    return render(request, 'contact/create_contact.html', {'form': form})
                
                # If we reach here, the user was created
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                user.set_password(make_password(password))
                user.save()    
                print(f"Password for {email} is: {password}")  # Log or send password

                # Add the user to the 'Contact' group
                contact_group = Group.objects.get(name='Contact')
                user.groups.add(contact_group)

                # Create the ContactDetail instance
                contact = form.save(commit=False)
                contact.user = user
                contact.created_by = request.user
                contact.updated_by = request.user
                contact.save()

                   # Process tags
                for tag_name in combined_tags:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)  # Create tag if not exists
                    contact.tags.add(tag)  # Add tag to contact
                

                messages.success(request, "Contact created successfully.")
                return redirect('contact_list')

            except Exception as e:
                # Generic exception handling, you might want to be more specific
                messages.error(request, f"An error occurred: {str(e)}")
                return render(request, 'contact/create_contact.html', {'form': form})

    else:
        form = ContactDetailCreationForm()
    return render(request, 'contact/create_contact.html', {'form': form})

