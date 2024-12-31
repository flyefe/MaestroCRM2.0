# from django import forms
# from django.contrib.auth.models import User, Group, Permission
# from django.contrib.auth.forms import UserCreationForm


# class UserEditForm(forms.ModelForm):
#     groups = forms.ModelMultipleChoiceField(
#         queryset=Group.objects.all(),
#         required=False,
#         widget=forms.CheckboxSelectMultiple,
#         label="Roles (Groups)"
#     )
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name', 'groups']


# class RoleEditForm(forms.ModelForm):
#     permissions = forms.ModelMultipleChoiceField(
#         queryset=Permission.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

#     class Meta:
#         model = Group
#         fields = ['name', 'permissions']
#         labels = {
#             'name': 'Role Name',
#             'permissions': 'Assign Permissions'
#         }

# class RoleCreationForm(forms.ModelForm):
#     permissions = forms.ModelMultipleChoiceField(
#         queryset=Permission.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

#     class Meta:
#         model = Group
#         fields = ['name', 'permissions']
#         widgets = {}
#         labels = {
#             'name': 'Role Name',
#             'permissions': 'Assign Permissions'
#         }


# # class RegisterForm(UserCreationForm):

# #     class Meta:
# #         model = User
# #         fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

# # forms.py
# from django import forms
# from django.contrib.auth.models import User

# class RegisterForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']
#         widgets = {
#             'username': forms.TextInput(attrs={
#                 'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
#                 'placeholder': 'Enter your username'
#             }),
#             'email': forms.EmailInput(attrs={
#                 'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
#                 'placeholder': 'Enter your email'
#             }),
#             'password': forms.PasswordInput(attrs={
#                 'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
#                 'placeholder': 'Enter your password'
#             }),
#         }


from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError

class UserEditForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'p-2 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring- focus:ring-gray-300'
        }),
        label="Roles (Groups)"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'groups']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
                'placeholder': 'Enter email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
                'placeholder': 'Enter last name'
            }),
        }


class RoleEditForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'p-2 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300'
        }),
        required=False,
        label="Assign Permissions"
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
                'placeholder': 'Enter role name'
            }),
        }
        labels = {
            'name': 'Role Name',
            'permissions': 'Assign Permissions'
        }


class RoleCreationForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'p-2 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300'
        }),
        required=False,
        label="Assign Permissions"
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
                'placeholder': 'Enter role name'
            }),
        }
        labels = {
            'name': 'Role Name',
            'permissions': 'Assign Permissions'
        }


# class SignUpForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput(
#         attrs={
#             'class':
#             'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
#             'placeholder': 'Enter your password'
#         }))

#     confirm_password = forms.CharField(widget=forms.PasswordInput(
#         attrs={
#             'class':
#             'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
#             'placeholder': 'Confirm your password'
#         }))

#     class Meta:
#         model = User
#         fields = ['email', 'first_name', 'last_name']
#         widgets = {
#             'email':
#             forms.EmailInput(
#                 attrs={
#                     'class':
#                     'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
#                     'placeholder': 'Enter your email'
#                 }),
#             'first_name':
#             forms.TextInput(
#                 attrs={
#                     'class':
#                     'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
#                     'placeholder': 'Enter your first name'
#                 }),
#             'last_name':
#             forms.TextInput(
#                 attrs={
#                     'class':
#                     'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
#                     'placeholder': 'Enter your last name'
#                 }),
#         }
#     def __init__(self, *args, **kwargs):
#             super(SignUpForm, self).__init__(*args, **kwargs)
#             self.fields['last_name'].required = True  # Make last_name required
#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get('password')
#         confirm_password = cleaned_data.get('confirm_password')

#         if password and confirm_password:
#             if password != confirm_password:
#                 raise ValidationError("Passwords do not match.")
#         return cleaned_data

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.username = self.cleaned_data['email']  # Set username to email
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#         return user


from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
            'placeholder': 'Enter your password'
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
                'placeholder': 'Enter your email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
                'placeholder': 'Enter your last name'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_name'].required = True

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data