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
@role_required(['Admin'])
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

@role_required(['Admin'])
def save_mapped_data(request):
    if 'csv_data' not in request.session or 'header_mapping' not in request.session:
        messages.error(request, "No mapping data found. Please re-upload the file.")
        return redirect('import_contacts')

    csv_data = request.session['csv_data']
    header_mapping = request.session['header_mapping']

    # Generate a unique tag for this import
    import_tag_name = f"import({datetime.now().strftime('%Y-%m-%d')})"
    import_tag, _ = Tag.objects.get_or_create(name=import_tag_name)

    try:
        for row in csv_data:
            contact_data = {}
            tags = []  # Initialize tags list

            # Process fields based on mapping
            for csv_column, model_field in header_mapping.items():
                value = row.get(csv_column, None)
                value = value.strip() if value else ""  # Handle None or empty values

                if model_field == 'first_name':
                    contact_data['first_name'] = value
                elif model_field == 'middle_name':
                    contact_data['middle_name'] = value
                elif model_field == 'last_name':
                    contact_data['last_name'] = value
                elif model_field == 'email':
                    contact_data['email'] = value
                elif model_field == 'date_of_birth':
                    try:
                        contact_data[model_field] = datetime.strptime(value, '%Y-%m-%d').date() if value else None
                    except ValueError:
                        messages.warning(request, f"Invalid date format for '{csv_column}'. Row skipped.")
                        continue
                elif model_field == 'services':
                    if value:
                        service, _ = Service.objects.get_or_create(name=value)
                        contact_data['services'] = service
                elif model_field == 'tags':
                    tag_names = [tag.strip() for tag in value.split(',')] if value else []
                    tags = [Tag.objects.get_or_create(name=tag_name)[0] for tag_name in tag_names]
                elif model_field == 'status':
                    if value:
                        status, _ = Status.objects.get_or_create(name=value)
                        contact_data['status'] = status
                    else:
                        status, _ = Status.objects.get_or_create(name='Lead')
                        contact_data['status'] = status
                elif model_field == 'traffic_source':
                    if value:
                        traffic_source, _ = TrafficSource.objects.get_or_create(name=value)
                        contact_data['traffic_source'] = traffic_source
                elif model_field == 'new_or_old':
                    contact_data[model_field] = value if value in ['New', 'Old'] else None
                elif model_field == 'log':
                    contact_data['log'] = value
                elif model_field == 'assigned_staff':
                    if value:
                        name_parts = value.split()
                        assigned_staff = None
                        try:
                            if len(name_parts) == 1:
                                assigned_staff = User.objects.filter(
                                    groups__name='Staff'
                                ).filter(
                                    Q(first_name__iexact=name_parts[0]) | Q(last_name__iexact=name_parts[0])
                                ).first()
                            elif len(name_parts) == 2:
                                assigned_staff = User.objects.filter(
                                    groups__name='Staff'
                                ).filter(
                                    first_name__iexact=name_parts[0],
                                    last_name__iexact=name_parts[1]
                                ).first()
                            if assigned_staff:
                                contact_data[model_field] = assigned_staff
                            else:
                                messages.warning(request, f"Assigned staff '{value}' not found. Row skipped.")
                                continue
                        except Exception as e:
                            messages.error(request, f"Error assigning staff for value '{value}': {e}")
                            continue
                elif model_field:  # Any other mapped fields
                    contact_data[model_field] = value

            # Create or update the Contact
            try:
                contact, contact_created = Contact.objects.get_or_create(
                    first_name=contact_data.get('first_name', ""),
                    last_name=contact_data.get('last_name', ""),
                    phone_number=contact_data.get('phone_number', ""),
                    defaults={key: value for key, value in contact_data.items() if key not in ['log', 'tags']}
                )
                if not contact_created:
                    for key, value in contact_data.items():
                        if key != 'log':
                            setattr(contact, key, value)
                    contact.save()

                # Set tags after contact creation
                if tags:
                    contact.tags.set(tags)

                # Add the import tag to the contact
                contact.tags.add(import_tag)

                # Process logs
                log_value = contact_data.get('log', "")
                if log_value:
                    Log.objects.create(
                        contact=contact,
                        log_type='feedback',
                        log_title=log_value,
                        log_description="",
                        created_by=request.user
                    )
            except Exception as e:
                messages.error(request, f"Error creating/updating contact: {e}")
                continue

        # Clear session data
        del request.session['csv_data']
        del request.session['csv_headers']
        del request.session['header_mapping']

        messages.success(request, f"Contacts imported successfully with tag: {import_tag_name}")
        return redirect('contact_list')

    except Exception as e:
        messages.error(request, f"Error saving data: {e}")
        return redirect('import_contacts')
