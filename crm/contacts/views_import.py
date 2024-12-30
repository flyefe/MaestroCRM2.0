import csv
from django.db.models import Q
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact
from .forms import ContactImportForm, FieldMappingForm

from datetime import datetime
from django.contrib.auth.models import User, Group
from .models import Contact, Log

from settings.models import Service, TrafficSource, Tag, Status

from django.contrib.auth.decorators import login_required

from core.decorators import role_required



#Assign import to status, created_by, Tag, Contact Role, Staff, etc


# View 1: Import CSV File
@role_required(['Admin'])
def import_contacts(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            # Step 1: Handle CSV Upload
            csv_file = request.FILES['file']
            try:
                # Read CSV file
                file_data = csv_file.read().decode("utf-8-sig").splitlines()
                reader = csv.DictReader(file_data)
                headers = reader.fieldnames

                # Save headers and data in session
                request.session['csv_headers'] = headers
                request.session['csv_data'] = list(reader)

                return redirect('map_fields')

            except Exception as e:
                messages.error(request, f"Error processing the file: {e}")
                return redirect('import_contacts')
        else:
            messages.error(request, "No file uploaded.")
            return redirect('import_contacts')

    else:
        form = ContactImportForm()

    return render(request, 'import/import_contacts.html', {'form': form})


# View 2: Map CSV Headers to Contact Fields
def map_fields(request):
    if 'csv_headers' not in request.session:
        messages.error(request, "No CSV headers found. Please upload the file again.")
        return redirect('import_contacts')

    csv_headers = request.session['csv_headers']

    
    # Fetch all contact fields dynamically
    # contact_fields = ['first_name', 'last_name', 'email'] + [field.name for field in Contact._meta.get_fields()]
    contact_fields = [
        'first_name',
        'middle_name',
        'last_name', 
        'email', 
        'phone_number', 
        'gender', 
        'marital_status',
        'date_of_birth',
        'services',
        'status',
        'tags',
        'traffic_source',
        'new_or_old',
        'assigned_staff',
        'log',
    ]

    # Step 3: Create the dynamic form for field mapping
    class FieldMappingForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for header in csv_headers:
                self.fields[header] = forms.ChoiceField(
                    choices=[('', '----')] + [(field, field) for field in contact_fields],
                    required=False,
                    label=header
                )

    if request.method == "POST":
        form = FieldMappingForm(request.POST)
        if form.is_valid():
            # Save mapping to session
            request.session['header_mapping'] = form.cleaned_data
            return redirect('save_mapped_data')

    else:
        form = FieldMappingForm()

    return render(request, 'import/map_fields.html', {'form': form, 'csv_headers': csv_headers})


def save_mapped_data(request):
    if 'csv_data' not in request.session or 'header_mapping' not in request.session:
        messages.error(request, "No mapping data found. Please re-upload the file.")
        return redirect('import_contacts')

    csv_data = request.session['csv_data']
    header_mapping = request.session['header_mapping']

    # Generate a unique tag for this import
    import_tag_name = f"import({datetime.now().strftime('%Y-%m-%d')})"
    import_tag, _ = Tag.objects.get_or_create(name=import_tag_name)

    contact_fields = [
        'first_name',
        'middle_name',
        'last_name', 
        'email', 
        'phone_number', 
        'gender', 
        'marital_status',
        'date_of_birth',
        'services',
        'status',
        'tags',
        'traffic_source',
        'new_or_old',
        'assigned_staff',
        'log',
    ]

    try:
        for row in csv_data:
            contact_data = {}
            first_name = middle_name = last_name = email = None
            tags = []  # Initialize tags list

            # Process fields based on mapping
            for csv_column, model_field in header_mapping.items():
                value = row.get(csv_column, "").strip()

                if model_field == 'first_name':
                    first_name = value
                elif model_field == 'middle_name':
                    middle_name = value
                    contact_data[model_field] = middle_name
                elif model_field == 'last_name':
                    last_name = value
                elif model_field == 'email':
                    email = value
                elif model_field == 'date_of_birth':
                    # Parse date
                    try:
                        contact_data[model_field] = datetime.strptime(value, '%Y-%m-%d').date() if value else None
                    except ValueError:
                        messages.error(request, f"Invalid date format for '{csv_column}'. Expected 'YYYY-MM-DD'. Row skipped.")
                        continue
                elif model_field == 'services':
                    # Handle services
                    if value:
                        service, _ = Service.objects.get_or_create(name=value)
                        contact_data['services'] = service

                elif model_field == 'tags':
                    # Handle tags
                    tag_names = [tag.strip() for tag in value.split(',')] if value else []
                    tags = [Tag.objects.get_or_create(name=tag_name)[0] for tag_name in tag_names]
                
                elif model_field == 'status':
                    # Handle ForeignKey to Status
                    if value:
                        status, _ = Status.objects.get_or_create(name=value)
                        contact_data['status'] = status
                    else:
                        # Default to 'Lead' when not specified
                        status, _ = Status.objects.get_or_create(name='Lead')
                    contact_data['status'] = status
                   
                elif model_field == 'traffic_source':
                    # Handle traffic sources
                    if value:
                        traffic_source, _ = TrafficSource.objects.get_or_create(name=value)
                        contact_data['traffic_source'] = traffic_source
                elif model_field == 'new_or_old':
                    # Handle choice field
                    contact_data[model_field] = value if value in ['New', 'Old'] else None
                elif model_field == 'log':
                    # Logs are created separately, process them after saving the contact
                    contact_data['log'] = value  # Stash for later processing

                elif model_field == 'assigned_staff':
                    # Handle assigning specific staff based on first name and/or last name
                    if value:  # If a value is provided in the CSV
                        try:
                            # Split the value to search by first and last name
                            name_parts = value.split()
                            if len(name_parts) == 1:
                                # Search by first name or last name if only one part is provided
                                assigned_staff = User.objects.filter(
                                    groups__name='Staff'
                                ).filter(
                                    Q(first_name__iexact=name_parts[0]) | Q(last_name__iexact=name_parts[0])
                                ).first()
                            elif len(name_parts) == 2:
                                # Search by both first name and last name if both are provided
                                assigned_staff = User.objects.filter(
                                    groups__name='Staff'
                                ).filter(
                                    first_name__iexact=name_parts[0],
                                    last_name__iexact=name_parts[1]
                                ).first()
                            else:
                                assigned_staff = None  # If the value doesn't match expected formats, set to None

                            if assigned_staff:
                                contact_data[model_field] = assigned_staff
                            else:
                                messages.error(
                                    request, f"Assigned staff '{value}' not found. Row skipped."
                                )
                                continue

                        except Exception as e:
                            messages.error(
                                request, f"Error assigning staff for value '{value}': {e}"
                            )
                            continue
                elif model_field:  # Other fields
                    contact_data[model_field] = value

            # Ensure email is provided
            if not email:
                messages.error(request, f"Row skipped: Missing email address.")
                continue

            # Create or update the User
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'first_name': first_name or "",
                    'last_name': last_name or "",
                }
            )
            
            if not created:
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name

            # Add user account to contact group
            contact_group = Group.objects.get(name='Contact')
            user.groups.add(contact_group)
            user.save()

            # Create or update Contact
            contact, contact_created = Contact.objects.get_or_create(
                user=user,
                defaults={key: value for key, value in contact_data.items() if key != 'log'}
            )
            if not contact_created:
                for key, value in contact_data.items():
                    if key == 'tags':
                        # Set tags using set() method to avoid direct assignment
                        contact.tags.set(tags)  # Correct usage here
                    elif key != 'log':
                        setattr(contact, key, value)
                 # Ensure default status is applied if not already set
                if not contact.status:
                    default_status, _ = Status.objects.get(name='Lead')
                    contact.status = default_status
                contact.save()

            # Process logs if provided
            log_value = contact_data.get('log')
            if log_value:
                try:
                    Log.objects.create(
                        contact=contact,
                        log_type='feedback',  # Default log type
                        log_title=log_value,  # Use the value as the title
                        log_description="",   # Leave the description empty
                        created_by=request.user
                    )
                except Exception as e:
                    messages.error(request, f"Error creating log for contact {email}: {e}")
            
            #  #Add status to all without status
            # if status == None:
            #     status = Status.objects.get(name='Lead')
            #     contact.status.add(status)
            
            # After the contact has been created or updated, now assign the tags using `set()`
            if tags:
                contact.tags.set(tags)  # Correctly set the tags using `set()`


            # Add the import tag to the contact
            contact.tags.add(import_tag)

        # Clear session data
        del request.session['csv_data']
        del request.session['csv_headers']
        del request.session['header_mapping']

        messages.success(request, f"Contacts imported successfully with tag: {import_tag_name}")
        return redirect('contact_list')

    except Exception as e:
        messages.error(request, f"Error saving data: {e}")
        return redirect('import_contacts')


# def save_mapped_data(request):
#     if 'csv_data' not in request.session or 'header_mapping' not in request.session:
#         messages.error(request, "No mapping data found. Please re-upload the file.")
#         return redirect('import_contacts')

#     csv_data = request.session['csv_data']
#     header_mapping = request.session['header_mapping']

#     # Generate a unique tag for this import
#     import_tag_name = f"import({datetime.now().strftime('%Y-%m-%d')})"
#     import_tag, _ = Tag.objects.get_or_create(name=import_tag_name)

#     contact_fields = [
#         'first_name',
#         'middle_name',
#         'last_name', 
#         'email', 
#         'phone_number', 
#         'gender', 
#         'marital_status',
#         'date_of_birth',
#         'services',
#         'status',
#         'tags',
#         'traffic_source',
#         'new_or_old',
#         'log',
#     ]

#     try:
#         for row in csv_data:
#             contact_data = {}
#             first_name = middle_name = last_name = email = None

#             # Process fields based on mapping
#             for csv_column, model_field in header_mapping.items():
#                 value = row.get(csv_column, "").strip()

#                 if model_field == 'first_name':
#                     first_name = value
#                 elif model_field == 'middle_name':
#                     middle_name = value
#                 elif model_field == 'last_name':
#                     last_name = value
#                 elif model_field == 'email':
#                     email = value
#                 elif model_field == 'date_of_birth':
#                     # Parse date
#                     try:
#                         contact_data[model_field] = datetime.strptime(value, '%Y-%m-%d').date() if value else None
#                     except ValueError:
#                         messages.error(request, f"Invalid date format for '{csv_column}'. Expected 'YYYY-MM-DD'. Row skipped.")
#                         continue
#                 elif model_field == 'services':
#                     # Handle services
#                     if value:
#                         service, _ = Service.objects.get_or_create(name=value)
#                         contact_data['services'] = service

#                 elif model_field == 'tags':
#                     # Handle tags
#                     tag_names = [tag.strip() for tag in value.split(',')] if value else []
#                     tags = [Tag.objects.get_or_create(name=tag_name)[0] for tag_name in tag_names]
#                     # contact_data['tags'] = tags
                
#                 elif model_field == 'status':
#                     # Handle ForeignKey to Status
#                     try:
#                         contact_data[model_field] = Status.objects.get_or_create(name=value)[0] if value else None
#                     except Status.DoesNotExist:
#                         messages.error(request, f"Status '{value}' does not exist. Row skipped.")
#                         continue
#                 elif model_field == 'traffic_source':
#                     # Handle traffic sources
#                     if value:
#                         traffic_source, _ = TrafficSource.objects.get_or_create(name=value)
#                         contact_data['traffic_source'] = traffic_source
#                 elif model_field == 'new_or_old':
#                     # Handle choice field
#                     contact_data[model_field] = value if value in ['New', 'Old'] else None
#                 elif model_field == 'log':
#                     # Logs are created separately, process them after saving the contact
#                     contact_data['log'] = value  # Stash for later processing
#                 elif model_field:  # Other fields
#                     contact_data[model_field] = value

#             # Ensure email is provided
#             if not email:
#                 messages.error(request, f"Row skipped: Missing email address.")
#                 continue

#             # Create or update the User
#             user, created = User.objects.get_or_create(
#                 username=email,
#                 defaults={
#                     'email': email,
#                     'first_name': first_name or "",
#                     'last_name': last_name or "",
#                 }
#             )
            
#             if not created:
#                 user.first_name = first_name or user.first_name
#                 user.last_name = last_name or user.last_name

#             # Add user account to contact group
#             contact_group = Group.objects.get(name='Contact')
#             user.groups.add(contact_group)
#             user.save()

#             # Create or update Contact
#             contact, contact_created = Contact.objects.get_or_create(
#                 user=user,
#                 defaults={key: value for key, value in contact_data.items() if key != 'log'}
#             )
#             if not contact_created:
#                 for key, value in contact_data.items():
#                     if key == 'tags':
#                         contact.tags.set(value)  # Correct usage here
#                     elif key != 'log':
#                         setattr(contact, key, value)
#                 contact.save()

#             # Process logs if provided
#             log_value = contact_data.get('log')
#             if log_value:
#                 try:
#                     Log.objects.create(
#                         contact=contact,
#                         log_type='feedback',  # Default log type
#                         log_title=log_value,  # Use the value as the title
#                         log_description="",   # Leave the description empty
#                         created_by=request.user
#                     )
#                 except Exception as e:
#                     messages.error(request, f"Error creating log for contact {email}: {e}")

#             # Add the import tag to the contact
#             contact.tags.add(import_tag)

#         # Clear session data
#         del request.session['csv_data']
#         del request.session['csv_headers']
#         del request.session['header_mapping']

#         messages.success(request, f"Contacts imported successfully with tag: {import_tag_name}")
#         return redirect('contact_list')

#     except Exception as e:
#         messages.error(request, f"Error saving data: {e}")
#         return redirect('import_contacts')


# def save_mapped_data(request):
#     if 'csv_data' not in request.session or 'header_mapping' not in request.session:
#         messages.error(request, "No mapping data found. Please re-upload the file.")
#         return redirect('import_contacts')

#     csv_data = request.session['csv_data']
#     header_mapping = request.session['header_mapping']

#     # Generate a unique tag for this import
#     import_tag_name = f"import({datetime.now().strftime('%Y-%m-%d')})"
#     import_tag, _ = Tag.objects.get_or_create(name=import_tag_name)

#     contact_fields = [
#         'first_name',
#         'middle_name',
#         'last_name', 
#         'email', 
#         'phone_number', 
#         'gender', 
#         'marital_status',
#         'date_of_birth',
#         'services',
#         'status',
#         'tags',
#         'traffic_source',
#         'new_or_old',
#         'log',
#     ]

#     try:
#         for row in csv_data:
#             contact_data = {}
#             first_name = middle_name = last_name = email = None
#             tags = []

#             # Process fields based on mapping
#             for csv_column, model_field in header_mapping.items():
#                 value = row.get(csv_column, "").strip()

#                 if model_field == 'first_name':
#                     first_name = value
#                 elif model_field == 'middle_name':
#                     middle_name = value
#                 elif model_field == 'last_name':
#                     last_name = value
#                 elif model_field == 'email':
#                     email = value
#                 elif model_field == 'date_of_birth':
#                     # Parse date
#                     try:
#                         contact_data[model_field] = datetime.strptime(value, '%Y-%m-%d').date() if value else None
#                     except ValueError:
#                         messages.error(request, f"Invalid date format for '{csv_column}'. Expected 'YYYY-MM-DD'. Row skipped.")
#                         continue
#                 elif model_field == 'services':
#                     # Handle services
#                     if value:
#                         service, _ = Service.objects.get_or_create(name=value)
#                         contact_data['services'] = service

#                 elif model_field == 'tags':
#                     # Handle tags
#                     tag_names = [tag.strip() for tag in value.split(',')] if value else []
#                     tags = [Tag.objects.get_or_create(name=tag_name)[0] for tag_name in tag_names]
                
#                 elif model_field == 'status':
#                     # Handle ForeignKey to Status
#                     if value:
#                         status, _ = Status.objects.get_or_create(name=value)
#                         contact_data['status'] = status
#                     else:
#                         status = Status.objects.get(name='Lead')
                   
#                 elif model_field == 'traffic_source':
#                     # Handle traffic sources
#                     if value:
#                         traffic_source, _ = TrafficSource.objects.get_or_create(name=value)
#                         contact_data['traffic_source'] = traffic_source
#                 elif model_field == 'new_or_old':
#                     # Handle choice field
#                     contact_data[model_field] = value if value in ['New', 'Old'] else None
#                 elif model_field == 'log':
#                     # Logs are created separately, process them after saving the contact
#                     contact_data['log'] = value  # Stash for later processing
#                 elif model_field:  # Other fields
#                     contact_data[model_field] = value

#             # Ensure email is provided
#             if not email:
#                 messages.error(request, f"Row skipped: Missing email address.")
#                 continue

#             # Create or update the User
#             user, created = User.objects.get_or_create(
#                 username=email,
#                 defaults={
#                     'email': email,
#                     'first_name': first_name or "",
#                     'last_name': last_name or "",
#                 }
#             )
            
#             if not created:
#                 user.first_name = first_name or user.first_name
#                 user.last_name = last_name or user.last_name

#             # Add user account to contact group
#             contact_group = Group.objects.get(name='Contact')
#             user.groups.add(contact_group)
#             user.save()

#             # Create or update Contact
#             contact, contact_created = Contact.objects.get_or_create(
#                 user=user,
#                 defaults={key: value for key, value in contact_data.items() if key != 'log'}
#             )
#             if not contact_created:
#                 for key, value in contact_data.items():
#                     if key == 'tags':
#                         # Set tags using set() method to avoid direct assignment
#                         contact.tags.set(tags)  # Correct usage here
#                     elif key != 'log':
#                         setattr(contact, key, value)
#                 contact.save()

#             # Process logs if provided
#             log_value = contact_data.get('log')
#             if log_value:
#                 try:
#                     Log.objects.create(
#                         contact=contact,
#                         log_type='feedback',  # Default log type
#                         log_title=log_value,  # Use the value as the title
#                         log_description="",   # Leave the description empty
#                         created_by=request.user
#                     )
#                 except Exception as e:
#                     messages.error(request, f"Error creating log for contact {email}: {e}")

#             # Add the import tag to the contact
#             contact.tags.add(import_tag)

#         # Clear session data
#         del request.session['csv_data']
#         del request.session['csv_headers']
#         del request.session['header_mapping']

#         messages.success(request, f"Contacts imported successfully with tag: {import_tag_name}")
#         return redirect('contact_list')

#     except Exception as e:
#         messages.error(request, f"Error saving data: {e}")
#         return redirect('import_contacts')



# def save_mapped_data(request):
#     if 'csv_data' not in request.session or 'header_mapping' not in request.session:
#         messages.error(request, "No mapping data found. Please re-upload the file.")
#         return redirect('import_contacts')

#     csv_data = request.session['csv_data']
#     header_mapping = request.session['header_mapping']

#     # Generate a unique tag for this import
#     import_tag_name = f"import({datetime.now().strftime('%Y-%m-%d')})"
#     import_tag, _ = Tag.objects.get_or_create(name=import_tag_name)

#     try:
#         for row in csv_data:
#             # Extract fields based on mapping
#             contact_data = {}
#             first_name = last_name = email = None

#             for csv_column, model_field in header_mapping.items():
#                 value = row.get(csv_column, "").strip()
#                 if model_field == 'first_name':
#                     first_name = value
#                 elif model_field == 'last_name':
#                     last_name = value
#                 elif model_field == 'email':
#                     email = value
#                 elif model_field:  # All other fields
#                     contact_data[model_field] = value

#             # Ensure email is provided
#             if not email:
#                 messages.error(request, f"Row skipped: Missing email address.")
#                 continue

#             # Create or update the user
#             user, created = User.objects.get_or_create(
#                 username=email,
#                 defaults={
#                     'email': email,
#                     'first_name': first_name or "",
#                     'last_name': last_name or "",
#                 }
#             )
#             if not created:
#                 # Update user's first_name and last_name if needed
#                 user.first_name = first_name or user.first_name
#                 user.last_name = last_name or user.last_name
#                 user.save()

#             # Check if a Contact already exists for this user
#             contact, contact_created = Contact.objects.get_or_create(
#                 user=user,
#                 defaults=contact_data  # Only used if the contact is new
#             )

#             if not contact_created:
#                 # Update existing Contact with new data
#                 for key, value in contact_data.items():
#                     setattr(contact, key, value)
#                 contact.save()

#             # Add the import tag to the contact
#             contact.tags.add(import_tag)

#         # Clear session data
#         del request.session['csv_data']
#         del request.session['csv_headers']
#         del request.session['header_mapping']

#         messages.success(request, f"Contacts imported successfully with tag: {import_tag_name}")
#         return redirect('contact_list')

#     except Exception as e:
#         messages.error(request, f"Error saving data: {e}")
#         return redirect('import_contacts')
