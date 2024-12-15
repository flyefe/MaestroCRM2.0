import csv
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactDetail
from .forms import ContactImportForm, FieldMappingForm

from datetime import datetime
from django.contrib.auth.models import User
from .models import ContactDetail, Tag

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


# View 2: Map CSV Headers to ContactDetail Fields
def map_fields(request):
    if 'csv_headers' not in request.session:
        messages.error(request, "No CSV headers found. Please upload the file again.")
        return redirect('import_contacts')

    csv_headers = request.session['csv_headers']

    
    # Fetch all contact fields dynamically
    contact_fields = ['first_name', 'last_name', 'email'] + [field.name for field in ContactDetail._meta.get_fields()]
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

    try:
        for row in csv_data:
            # Extract fields based on mapping
            contact_data = {}
            first_name = last_name = email = None

            for csv_column, model_field in header_mapping.items():
                value = row.get(csv_column, "").strip()
                if model_field == 'first_name':
                    first_name = value
                elif model_field == 'last_name':
                    last_name = value
                elif model_field == 'email':
                    email = value
                elif model_field:  # All other fields
                    contact_data[model_field] = value

            # Ensure email is provided
            if not email:
                messages.error(request, f"Row skipped: Missing email address.")
                continue

            # Create or update the user
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'first_name': first_name or "",
                    'last_name': last_name or "",
                }
            )
            if not created:
                # Update user's first_name and last_name if needed
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                user.save()

            # Check if a ContactDetail already exists for this user
            contact, contact_created = ContactDetail.objects.get_or_create(
                user=user,
                defaults=contact_data  # Only used if the contact is new
            )

            if not contact_created:
                # Update existing ContactDetail with new data
                for key, value in contact_data.items():
                    setattr(contact, key, value)
                contact.save()

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

