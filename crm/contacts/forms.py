from django import forms
from django.contrib.auth.models import User, Group
from django.db.models import Q  # Import Q here
from .models import Contact, Log
from settings.models import TrafficSource, Service, Status,Tag

from django_select2.forms import Select2Widget, ModelSelect2Widget



from django import forms
from django.contrib.auth.models import User, Group
from .models import Status, Tag, Service, TrafficSource

from django import forms
from .models import Log, User, Contact



class ContactSearchForm(forms.Form):
    query = forms.CharField(
        label='Search',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
            'placeholder': 'Search for contacts...'
        })
    )


# class ContactFilterForm(forms.Form):
#     status = forms.ModelChoiceField(
#         queryset=Status.objects.all(),
#         required=False,
#         empty_label="All Statuses",
#         widget=forms.Select(attrs={"class": "text-sm border-gray-300 rounded py-2 px-3"})
#     )
#     tags = forms.ModelChoiceField(
#         queryset=Tag.objects.all(),
#         required=False,
#         empty_label="All Tags",
#         widget=forms.Select(attrs={"class": "text-sm border-gray-300 rounded py-2 px-3"})
#     )
#     services = forms.ModelChoiceField(
#         queryset=Service.objects.all(),
#         required=False,
#         empty_label="All Services",
#         widget=forms.Select(attrs={"class": "text-sm border-gray-300 rounded py-2 px-3"})
#     )
#     traffic_source = forms.ModelChoiceField(
#         queryset=TrafficSource.objects.all(),
#         required=False,
#         empty_label="All Traffic Sources",
#         widget=forms.Select(attrs={"class": "text-sm border-gray-300 rounded py-2 px-3"})
#     )

#     assigned_staff = forms.ModelChoiceField(
#         queryset=User.objects.filter(assigned_contacts__isnull=False).distinct(),
#         # queryset=User.objects.filter(Q(is_staff=True) | Q(groups__name="Staff")).distinct(),
#         required=False,
#         label="Assigned Staff",
#         to_field_name="id",  # This is important to keep the correct ID
#         empty_label="Assigned Staff",
#         widget=forms.Select(attrs={'class': "text-sm border-gray-300 rounded py-2 px-3 form-control" }),

#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Customize the label for assigned_staff
#         self.fields['assigned_staff'].queryset = User.objects.filter(assigned_contacts__isnull=False).distinct()
#         self.fields['assigned_staff'].label_from_instance = lambda obj: f"{obj.get_full_name()}" if obj.get_full_name() else obj.username

from django import forms
from .models import Status, Tag, Service, TrafficSource
from django.contrib.auth.models import User
from django.db.models import Q

class ContactFilterForm(forms.Form):
    status = forms.ModelChoiceField(
        queryset=Status.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            "class": "text-sm border border-gray-300 rounded-md py-2 px-3 w-full bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "aria-label": "Filter by Status"
        }),
        empty_label="Search by Status",
        label=''
    )
    tags = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            "class": "text-sm border border-gray-300 rounded-md py-2 px-3 w-full bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "aria-label": "Filter by Tags"
        }),
        label='',
        empty_label="Search by Tag",
    )
    services = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            "class": "text-sm border border-gray-300 rounded-md py-2 px-3 w-full bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "aria-label": "Filter by Services"
        }),
        empty_label="Search by Service",
        label=''
    )
    traffic_source = forms.ModelChoiceField(
        queryset=TrafficSource.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            "class": "text-sm border border-gray-300 rounded-md py-2 px-3 w-full bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "aria-label": "Filter by Traffic Source"
        }),
        empty_label="Search by Traffic Source",
        label=''
    )

    assigned_staff = forms.ModelChoiceField(
        queryset=User.objects.filter(assigned_contacts__isnull=False).distinct(),
        required=False,
        to_field_name="id",
        widget=forms.Select(attrs={
            "class": "text-sm border border-gray-300 rounded-md py-2 px-3 w-full bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "aria-label": "Filter by Assigned Staff"
        }),
        empty_label="Search by Assigned Staff",
        label=''
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_staff'].label_from_instance = lambda obj: f"{obj.get_full_name()}" if obj.get_full_name() else obj.username


class ContactCreationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        label="First Name",
        required=True,
        widget=forms.TextInput(
            attrs={
                'class':
                'form-input block w-full rounded border border-black p-2 mb-2',
                'style': 'background-color: #f5f5f5;',
                'placeholder': 'First Name'
            }))
    middle_name = forms.CharField(max_length=30, label="Middle Name", required=False, widget=forms.TextInput(attrs={
            'class': 'form-input block w-full rounded border border-black p-2 mb-2',
            'style': 'background-color: #f5f5f5;',
            'placeholder': 'Middle Name'
        }))
    last_name = forms.CharField(
        max_length=30,
        label="Last Name",
        required=True,
        widget=forms.TextInput(
            attrs={
                'class':
                'form-input block w-full rounded border border-black p-2 mb-2',
                'style': 'background-color: #f5f5f5;',
                'placeholder': 'Last Name'
            }))
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class':
                'form-input block w-full rounded border border-black p-2 mb-2',
                'style': 'background-color: #f5f5f5;',
                'placeholder': 'Email'
            }))

    tag = forms.CharField(
        label="Tags",
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter tags separated by commas',
                'class':
                'form-input block w-full rounded border border-black p-2 mb-2',
                'style': 'background-color: #f5f5f5;',
            }),
        required=False,
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class':
                'p-2 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300'
            }),
        required=False,
        label="Assign Tags")

    referred_by = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Referred By",
        empty_label="Referred By",
        to_field_name="id",  # This is important to keep the correct ID
        widget=Select2Widget(
            attrs={
                'class':
                'form-select block w-full rounded border border-gray-700 p-2 mb-2',
                'style': 'background-color: #f5f5f5;',
                'data-placeholder':
                'Select a reference...',  # Placeholder for the dropdown
                'data-allow-clear':
                'true',  # Allow the user to clear their selection
                'data-minimum-results-for-search': '0',
            }),
        required=False)
    
   


    class Meta:
        model = Contact
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 'status', 'tags',
            'assigned_staff', 'phone_number', 'traffic_source', 'services',
            'referred_by', 'date_of_birth', 'address_line1', 'address_line2', 'city',
            'state', 'country', 'postal_code'
        ]
        widgets = {
            'status':
            forms.Select(
                attrs={
                    'class':
                    'form-select block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color: #f5f5f5;'
                }),
            'assigned_staff':
            Select2Widget(
                attrs={
                    'class':
                    'form-select block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color: #f5f5f5;'
                }),
            'phone_number':
            forms.TextInput(
                attrs={
                    'class':
                    'form-input block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color: #f5f5f5;'
                }),
            'traffic_source':
            forms.Select(
                attrs={
                    'class':
                    'form-select block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color: #f5f5f5;'
                }),
            'services':
            forms.Select(
                attrs={
                    'class':
                    'form-select block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color: #f5f5f5;'
                }),
            'date_of_birth':
            forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class':
                    'form-input block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color:#f5f5f5'
                }),
            'close_date':
            forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class':
                    'form-input block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color:#f5f5f5'
                }),
          
          
             # Address fields in the form
            'address_line1':
            forms.TextInput(
                attrs={
                    'class':
                    'form-input block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color:#f5f5f5',
                    'placeholder': 'Address Line 1'
                }),

            'address_line2':
            forms.TextInput(
                attrs={
                    'class':
                    'form-input block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color:#f5f5f5',
                    'placeholder': 'Address Line 2'
                }),

            'city':
            forms.TextInput(
                attrs={
                    'class':
                    'form-input block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color:#f5f5f5',
                    'placeholder': 'City/Town'
                }),

            'state':
            forms.TextInput(
                attrs={
                    'class':
                    'form-input block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color:#f5f5f5',
                    'placeholder': 'State/Province'
                }),

            'country':
            forms.TextInput(
                attrs={
                    'class':
                    'form-input block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color:#f5f5f5',
                    'placeholder': 'Country'
                }),

            'postal_code':
            forms.TextInput(
                attrs={
                    'class':
                    'form-input block w-full rounded border border-black p-2 mb-2',
                    'style': 'background-color:#f5f5f5',
                    'placeholder': 'Postal Code'
                }),              
        }

        # Set referred_by field to be not required within the Meta class
        # required = {
        #     'referred_by': False
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Restrict the assigned_staff choices to only staff, admin, or users in a specific group
        specific_group = Group.objects.get(
            name="Staff"
        )  # Replace "YourGroupName" with your specific group name
        self.fields['assigned_staff'].queryset = User.objects.filter(
            Q(is_staff=True) | Q(groups=specific_group)).distinct()
        self.fields[
            'assigned_staff'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"
        self.fields[
            'referred_by'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"

class LogForm(forms.ModelForm):
    class Meta:
        model = Log
        fields = [ 'log_type', 'log_title', 'log_description']
        labels = {
            'log_type': 'Log Type',
            'log_title': 'Log Title',
            'log_description': 'Description',
        }
        widgets = {
            'log_type': forms.Select(attrs={
                'class': 'form-select block w-full rounded border border-black p-2 mb-2',
                'style': 'background-color: #f5f5f5;'
            }),
            'log_title': forms.TextInput(attrs={
                'class': 'form-input block w-full rounded border border-black p-2 mb-2',
                'style': 'background-color: #f5f5f5;'
            }),
            'log_description': forms.Textarea(attrs={
                'class': 'form-textarea block w-full rounded border border-black p-2 mb-2',
                'style': 'background-color: #f5f5f5;',
                'rows': '4'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(LogForm, self).__init__(*args, **kwargs)
        # self.fields['contact'].queryset = Contact.objects.all()
        # self.fields['created_by'].queryset = User.objects.all()

class StatusForm(forms.ModelForm):
    name = forms.CharField(
        label='Status Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Customers',
            'class': 'form-input block w-full rounded border border-black p-2 mb-2 focus:ring focus:ring-gray-500',
            # 'class' : "border rounded-lg p-2 w-full focus:ring focus:ring-gray-200",
            'style': 'background-color: #f5f5f5;'}
        )
    )
    class Meta:
        model = Status  # Link the form to the Status model
        fields = ['name']  # List of fields to include in the form

class TagForm(forms.ModelForm):
    name = forms.CharField(
        label='Tag Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'VIP',
            'class': 'form-input block w-full rounded border border-black p-2 mb-2',
            'style': 'background-color: #f5f5f5;'}
        )
    )
    class Meta:
        model = Tag  # Link the form to the Status model
        fields = ['name']  # List of fields to include in the form

class ContactImportForm(forms.Form):
    file = forms.FileField()



# Fetch all contact fields dynamically
contact_fields = ['first_name', 'last_name', 'email'] + [field.name for field in Contact._meta.get_fields()]
class FieldMappingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for header in csv_headers:
            self.fields[header] = forms.ChoiceField(
                choices=[('', '----')] + [(field, field) for field in contact_fields],
                required=False,
                label=header
            )
