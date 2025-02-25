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
from .forms import ContactCreationForm, LogForm, ContactFilterForm, ContactSearchForm
from .models import Contact, Log
# from .utility import filter_contacts
from settings.models import Tag, Status, TrafficSource, Service
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.paginator import Paginator

from segments.utils import reevaluate_segments_for_contacts  # Import the helper function



@login_required
def contacts_by_service(request, service_id):
    # Get the service by ID
    service = get_object_or_404(Service, id=service_id)

    # Filter contacts by status
    contacts = Contact.objects.filter(services=service)

    # Add pagination (Optional)
    paginator = Paginator(contacts, 100)  # Show 10 contacts per page
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
    contacts = Contact.objects.filter(traffic_source=traffic_source)

    # Add pagination (Optional)
    paginator = Paginator(contacts, 100)  # Show 10 contacts per page
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
    contacts = Contact.objects.filter(assigned_staff=assigned_staff)

    # Add pagination (Optional)
    paginator = Paginator(contacts, 100)  # Show 10 contacts per page
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
    contacts = Contact.objects.filter(status=status)

    # Add pagination (Optional)
    paginator = Paginator(contacts, 100)  # Show 10 contacts per page
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
    contacts = Contact.objects.filter(tags=tag)  # Filter contacts by tag

    # Add pagination (Optional)
    paginator = Paginator(contacts, 100)  # Show 10 contacts per page
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
    contact = get_object_or_404(Contact, id=contact_id)

    # Fetch recent activities (assuming Log model has a ForeignKey to Contact)
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

    contact = get_object_or_404(Contact, id=contact_id)

    # Check if the user is trying to delete their own contact
    if contact.user == request.user:
        messages.error(request, "You cannot delete your own contact.")
        return redirect('contact_detail', contact_id=contact.id)

    # Delete the contact first
    contact.delete()

    # Then delete the associated user
    if contact.user:
        user = contact.user
        user.delete()

    messages.success(request, f"Contact '{contact.user.first_name}' and associated user account have been successfully deleted.")
    return redirect('contact_list')  # Redirect to contact list or another appropriate page



@login_required
def my_assigned_contacts(request):
    # Subquery to get the most recent log (type = 'feedback') title
    recent_feedback_log_title = Log.objects.filter(
        contact=OuterRef('pk'),  # Match the Log with the Contact
        log_type='feedback'      # Filter only feedback logs
    ).order_by('-created_at').values('log_title')[:1]  # Get the most recent log title

    # Subquery to get the most recent log (type = 'feedback') description
    recent_feedback_log_description = Log.objects.filter(
        contact=OuterRef('pk'),
        log_type='feedback'
    ).order_by('-created_at').values('log_description')[:1]  # Get the most recent log description

    # Add annotations for recent log title and description to Contact
    contacts = Contact.objects.select_related('user').filter(
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
    form = ContactCreationForm()
    filter_form = ContactFilterForm()
    search_form = ContactSearchForm()
    assigned_contacts = True
    user = request.user

    context = {
        'contacts': page_contacts,
        'form': form,
        'filter_form': filter_form,
        'search_form': search_form,
        'assigned_contacts' : assigned_contacts,
        'user' : user,
    }
    return render(request, 'contact/contact_list.html', context)

@login_required
def contact_list(request):
    # Subquery to get the most recent log (type = 'feedback') title
    recent_feedback_log_title = Log.objects.filter(
        contact=OuterRef('pk'),  # Match the Log with the Contact
        log_type='feedback'      # Filter only feedback logs
    ).order_by('-created_at').values('log_title')[:1]  # Get the most recent log title

    # Subquery to get the most recent log (type = 'feedback') description
    recent_feedback_log_description = Log.objects.filter(
        contact=OuterRef('pk'),
        log_type='feedback'
    ).order_by('-created_at').values('log_description')[:1]  # Get the most recent log description

    # Add annotations for recent log title and description to Contact
    contacts = Contact.objects.select_related('user').annotate(
        recent_feedback_log_title=Coalesce(Subquery(recent_feedback_log_title, output_field=CharField()), Value('No Feedback')),
        recent_feedback_log_description=Coalesce(Subquery(recent_feedback_log_description, output_field=CharField()), Value('No Description'))
    ).order_by('-modified_at')

    # Pagination
    paginator = Paginator(contacts, 200)  # Show 10 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)

    # Forms
    form = ContactCreationForm()
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
    contacts = Contact.objects.select_related('user').all()
    form = ContactCreationForm
    filter_form = ContactFilterForm(request.GET)
    search_form = ContactSearchForm(request.GET or None)
    query = request.GET.get('query', '').strip()
    # contacts = Contact.objects.all()

    if query:
        # Search across multiple fields
        contacts = contacts.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(middle_name__icontains=query)
            | Q(phone_number__icontains=query)
            | Q(status__name__icontains=query) | Q(tags__name__icontains=query)
            | Q(services__name__icontains=query)
            | Q(log__log_title__icontains=query)| Q(log__log_description__icontains=query)
            | Q(traffic_source__name__icontains=query)).distinct()

    # Pagination
    paginator = Paginator(contacts, 100)  # Show 5 contacts per page
    page_number = request.GET.get('page')
    page_contacts = paginator.get_page(page_number)

    context = {
        'search_form': search_form,
        'form': form,
        'contacts': page_contacts,  # Paginated results
        'query': query,
        'filter_form': filter_form
    }

    return render(request, 'contact/contact_list.html', context)

@login_required
def filter_contact(request):
    # Initialize form with GET data if available
    filter_form = ContactFilterForm(request.GET)

    #Pass in search form as well
    search_form = ContactSearchForm(request.GET or None)

    form = ContactCreationForm



    # Start with all contacts, then apply filters
    # contacts = Contact.objects.select_related('user').all()
    contacts = Contact.objects.select_related('user').all()



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

        
        # New filters for missing contact details
        if filter_form.cleaned_data.get('no_phone_number'):
            contacts = contacts.filter(Q(phone_number__isnull=True) | Q(phone_number=""))

        if filter_form.cleaned_data.get('no_email'):
            contacts = contacts.filter(Q(email__isnull=True) | Q(email=""))

        if filter_form.cleaned_data.get('no_phone_and_email'):
            contacts = contacts.filter(
                (Q(phone_number__isnull=True) | Q(phone_number="")) & 
                (Q(email__isnull=True) | Q(email=""))
            )


    # Pagination
    paginator = Paginator(contacts, 200)  # Show 5 contacts per page
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
        if not selected_contacts or not any(selected_contacts):
            messages.error(request, "No contacts selected.")
            return redirect("contact_list")

        # Fetch contacts queryset once
        contacts = Contact.objects.filter(id__in=selected_contacts)

        if not contacts.exists():
            messages.error(request, "No valid contacts found.")
            return redirect("contact_list")

        # Action: Update Status
        if action_type == "update_status":
            status_id = request.POST.get("status")
            if status_id:
                contacts.update(status_id=status_id)
                messages.success(request, "Status updated successfully!")
                reevaluate_segments_for_contacts(contacts)
            else:
                messages.error(request, "No status selected.")

        # Action: Add Tags
        elif action_type == "add_tags":
            tag_ids = request.POST.getlist("tags")
            if tag_ids:
                for contact in contacts:
                    contact.tags.add(*tag_ids)
                messages.success(request, "Tags added successfully!")
                reevaluate_segments_for_contacts(contacts)
            else:
                messages.error(request, "No tags provided or selected.")

        # Action: Remove Tags
        elif action_type == "remove_tags":
            tag_ids = request.POST.getlist("tags")
            if tag_ids:
                tags = Tag.objects.filter(id__in=tag_ids)
                for contact in contacts:
                    contact.tags.remove(*tags)
                messages.success(request, "Tags removed successfully!")
                reevaluate_segments_for_contacts(contacts)
            else:
                messages.error(request, "No tags provided or selected.")

        # Action: Delete Contacts
        elif action_type == "delete":
            for contact in contacts:
                if contact.user:  # Delete associated User account if it exists
                    contact.user.delete()
                contact.delete()
            messages.success(request, "Selected contacts deleted successfully!")
            # No reevaluation needed, as contacts are deleted

        # Action: Assign to Staff
        elif action_type == "assign_staff":
            assigned_staff_id = request.POST.get("assigned_staff")
            if assigned_staff_id:
                contacts.update(assigned_staff_id=assigned_staff_id)
                messages.success(request, "Contacts assigned to staff successfully!")
                reevaluate_segments_for_contacts(contacts)
            else:
                messages.error(request, "No staff provided or selected.")

        # Action: Update Traffic Source
        elif action_type == "traffic_source":
            traffic_source_id = request.POST.get("traffic_source")
            if traffic_source_id:
                contacts.update(traffic_source_id=traffic_source_id)
                messages.success(request, "Contacts traffic sources updated successfully!")
                # reevaluate_segments_for_contacts(contacts)
            else:
                messages.error(request, "No traffic source provided or selected.")

        # Action: Update Services
        elif action_type == "services":
            services_id = request.POST.get("services")
            if services_id:
                contacts.update(services_id=services_id)
                messages.success(request, "Contacts services updated successfully!")
                # reevaluate_segments_for_contacts(contacts)
            else:
                messages.error(request, "No service provided or selected.")

        else:
            messages.error(request, "Invalid action selected.")

        return redirect("contact_list")

    return redirect("contact_list")


@login_required
def create_user_account_for_contact(request, contact_id):
    # Retrieve the contact
    contact = get_object_or_404(Contact, id=contact_id)

    if contact.user:
        messages.error(request, "This contact already has a user account.")
        return redirect(reverse('contact_detail', args=[contact_id]))

    if contact.email:
        try:
            # Generate a random password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            email=contact.email


            # Create the user account
            user = User.objects.create_user(
                # username=f"{contact.first_name.lower()}.{contact.last_name.lower()}_{contact_id}",
                email=email,
                username=email,
                first_name=contact.first_name,
                last_name=contact.last_name,
                password=password
            )

            # Assign the user to the 'Contact' group
            contact_group = Group.objects.get(name='Contact')  # Ensure this group exists
            user.groups.add(contact_group)

            # Link the user account to the contact
            contact.user = user
            contact.save()

            # Optional: Log or notify the generated password
            # print(f"Password for {user.email}: {password}")  # Remove this in production
            messages.success(request, "User account created successfully. Password has been generated.")

        except Exception as e:
            messages.error(request, f"An error occurred while creating the user account: {str(e)}")
    else:
        messages.error(request, "contact has no email. Email is required to create an account")


    return redirect(reverse('contact_detail', args=[contact_id]))


@login_required
def update_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    user = contact.user  # This can be None

    if request.method == 'POST':
        form = ContactCreationForm(request.POST, instance=contact)
        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            # Extract and merge tags from both fields
            tags_from_text = [tag.strip().title() for tag in form.cleaned_data['tag'].split(',') if tag.strip()]
            tags_from_select = [tag.name.strip() for tag in form.cleaned_data['tags']]  # Multi-select field
            combined_tags = set(tags_from_text + tags_from_select)  # Remove duplicates

            if user:  # If a user exists, update user details
                if email != user.email:  # Check if the email has been changed
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

            messages.success(request, 'Contact details updated successfully.')
            return redirect(reverse('contact_detail', args=[contact.id]))
    else:
        # Populate the form with current contact details
        form_initial = {
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'tag': ', '.join(contact.tags.values_list('name', flat=True))
        }
        if user:  # If user exists, include their details in the form
            form_initial.update({
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            })

        form = ContactCreationForm(instance=contact, initial=form_initial)

    return render(request, 'contact/update_contact_detail.html', {'form': form})


@login_required
@transaction.atomic
def create_contact(request):
    if request.method == 'POST':
        form = ContactCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # tags = [tag.strip().title() for tag in form.cleaned_data['tags'].split(',') if tag.strip()]

            # Extract and merge tags from both fields
            tags_from_text = [tag.strip().title() for tag in form.cleaned_data['tag'].split(',') if tag.strip()]
            tags_from_select = [tag.name.strip() for tag in form.cleaned_data['tags']]  # Taking `tags` is a multi-select field
            combined_tags = set(tags_from_text + tags_from_select)  # Remove duplicates

            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

            try:
                user = None
                if email:
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

                    # Add the user to the 'Contact' group
                    contact_group = Group.objects.get(name='Contact')
                    user.groups.add(contact_group)

                # Create the Contact instance
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
        form = ContactCreationForm()
    return render(request, 'contact/create_contact.html', {'form': form})
