from django import forms
from django.contrib.auth.models import User
from .models import ContactDetail, TrafickSource, Status, Service
from django.db.models import Q

class ContactDetailCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300',
        'placeholder': 'Enter email'
    }))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300',
        'placeholder': 'Enter first name'
    }))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300',
        'placeholder': 'Enter last name'
    }))
    
    # Address Fields
    address_first_line = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300',
        'placeholder': 'Address Line 1'
    }))
    address_second_line = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300',
        'placeholder': 'Address Line 2'
    }))
    address_city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300',
        'placeholder': 'City'
    }))
    address_country = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300',
        'placeholder': 'Country'
    }))
    address_postal_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300',
        'placeholder': 'Postal Code'
    }))
    
    class Meta:
        model = ContactDetail
        fields = [
            'user',
            'status',
            'tags',
            'assigned_staff',
            'phone_number',
            'trafick_source',
            'services',
            'open_date',
            'close_date',
            'created_by',
            'updated_by',
            'address_first_line',
            'address_second_line',
            'address_city',
            'address_country',
            'address_postal_code'
        ]
        widgets = {
            'status': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300'
            }),
            'assigned_staff': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300'
            }),
            'trafick_source': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300'
            }),
            'services': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300'
            }),
            'open_date': forms.DateTimeInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300',
                'type': 'datetime-local'
            }),
            'close_date': forms.DateTimeInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300',
                'type': 'datetime-local'
            }),
            'created_by': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300'
            }),
            'updated_by': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring focus:ring-gray-300'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ContactDetailCreationForm, self).__init__(*args, **kwargs)
        # Restrict `assigned_staff` to admins, staff, or specified users
        self.fields['assigned_staff'].queryset = User.objects.filter(
            Q(is_staff=True) | Q(is_superuser=True) | Q(groups__name='AllowedGroup')  # Replace 'AllowedGroup' with your group name
        )
