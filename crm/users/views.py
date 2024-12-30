from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from django.contrib.auth.hashers import make_password
import random, string

from django.contrib import messages
from django.contrib.auth.models import User, Group

from .forms import UserEditForm, SignUpForm, RoleCreationForm,RoleEditForm

from django.core.paginator import Paginator
from django.db.models import Q  # Import the Q object




#Edit group
@login_required
def edit_group(request, group_id):
    # Check if the user has the appropriate permissions
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to edit groups.")
        return redirect('create_group')  # Redirect to the list of groups or another preferred page

    # Fetch the group to be edited
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        form = RoleEditForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f"Group '{group.name}' has been updated successfully.")
            return redirect('create_group')  # Redirect to a group list or desired page
    else:
        form = RoleEditForm(instance=group)

    return render(request, 'edit_role.html', {'form': form, 'group': group})



@login_required
def delete_group(request, group_id):
    # Check if the user has permission to delete a group
    if not request.user.has_perm('auth.delete_group'):  # Explicitly check for the 'delete group' permission
        messages.error(request, "You do not have permission to delete groups.")
        return redirect('create_group')  # Redirect to an appropriate page

    # Get the group to be deleted
    group = get_object_or_404(Group, id=group_id)

    # Delete the group and display a success message
    group.delete()
    messages.success(request, f"Group '{group.name}' has been deleted successfully.")
    return redirect('create_group')  # Redirect to the list of groups or another page


# group.users
@login_required
def users_in_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    users = group.user_set.all()  # Retrieve all users in the specified group

    context = {
        'group': group,
        'users': users
    }
    return render(request, 'users_in_group.html', context)

#Create Role
@login_required
def create_group(request):
    
    groups = Group.objects.all()

    if request.method == 'POST':
        form = RoleCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New role created successfully.')
            return redirect('create_group')  # Redirect to a page that lists groups or any desired page
    else:
        form = RoleCreationForm()

    context = {
        'form':form,
        'groups':groups
    }

    return render(request, 'create_role.html', context)



# Delete Users
@login_required
def delete_user(request, user_id):
    # Check if the user has the appropriate permissions
    
    # if not request.user.is_superuser:  # or another permission check
    if not request.user.has_perm('auth.delete_user'):
        messages.error(request, "You do not have permission to delete users.")
        return redirect('user_list')  # Redirect to an appropriate page

    # Get the user to be deleted
    user = get_object_or_404(User, id=user_id)

    # Prevent the logged-in user from deleting themselves
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('user_list')

    # Delete the user and display a success message
    user.delete()
    messages.success(request, f"User {user.username} has been deleted successfully.")
    return redirect('user_list')  # Redirect to the list of users or another page


#Edit Users
@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User has been editted successfully.')
            return redirect('staff_list')  # Redirect to a page that lists all users or any preferred page
    else:
        form = UserEditForm(instance=user)


    return render(request, 'edit_user.html', {
        'form': form,
        'user': user
    })



@login_required
def add_staff_user(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST)  # Instantiate form with POST data

        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            try:
                # Check if a user with this email already exists
                if User.objects.filter(email=email).exists():
                    messages.error(request, "A user with this email already exists.")
                    return render(request, 'add_staff_user.html', {'form': form})

                # Create a new user
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                user = User.objects.create_user(
                    username=email,  # Assuming email as username
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )

                # Add the user to the 'Staff' group
                staff_group = Group.objects.get(name='Staff')
                user.groups.add(staff_group)

                # Set is_staff to True for staff users
                user.is_staff = True
                user.save()

                messages.success(request, "Staff user added successfully.")
                print(f"Password for {email} is: {password}")  # Log password or send via email
                return redirect('staff_list')  # Assuming you have a URL named 'staff_list'

            except Group.DoesNotExist:
                messages.error(request, "Staff group does not exist.")
                return render(request, 'add_staff_user.html', {'form': form})

    else:
        form = UserEditForm()

    return render(request, 'add_staff_user.html', {'form': form})

@login_required
def staff_table(request):
    # Correct the group filters
    staff_group = Group.objects.filter(name='Staff')
    admin_group = Group.objects.filter(name='Admin')  # Correct the name to 'Admin'

    # Fetch users who belong to either 'Staff' or 'Admin' group
    users = (User.objects.filter(groups__in=staff_group) | User.objects.filter(groups__in=admin_group)).distinct()
    
    user_list = []  # This will hold user data with roles

    for user in users:
        groups = user.groups.all()  # Fetch all roles (groups) for each user
        contact_detail = getattr(user, 'Contact', None)  # Access the Contact instance if it exists        
        user_list.append({
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'roles': [group.name for group in groups],  # Add roles (group names)
            'date_joined': user.date_joined,
            'user_contact_id': contact_detail.id if contact_detail else None  # Safely get the Contact ID
        })

    paginator = Paginator(user_list, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_users = paginator.get_page(page_number)

    form = UserEditForm

    context = {
        'user_list': page_users,
        'form' : form
    }
    return render(request, 'staff_list.html', context)


#Users Table
@login_required
def users_table(request):
    staff_group = Group.objects.get(name='Staff')

    users = User.objects.exclude(groups=staff_group)  # Fetch all users
    user_list = []  # This will hold user data with roles

    for user in users:
        groups = user.groups.all()  # Fetch all roles (groups) for each user
        contact_detail = getattr(user, 'Contact', None)  # Access the Contact instance if it exists
        user_list.append({
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'roles': [group.name for group in groups],  # Add roles (group names)
            'date_joined': user.date_joined,
            'user_contact_id': contact_detail.id if contact_detail else None  # Safely get the Contact ID
        })

    paginator = Paginator(user_list, 200)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_users = paginator.get_page(page_number)

    form = UserEditForm

    context = {
        'user_list': page_users,
        'form' : form
    }
    return render(request, 'user_list.html', context)




@login_required
def users_bulk_action(request):
    if request.method == "POST":
        action_type = request.POST.get("action_type")
        selected_users = [user_id for user_id in request.POST.get("selected_users", "").split(',') if user_id.strip().isdigit()]


        # Ensure users are selected
        if not selected_users:
            messages.error(request, "No users selected.")
            return redirect("user_list")
        
        if action_type == "add_groups":
            group_ids = request.POST.getlist("groups")
            if group_ids:
                for user in User.objects.filter(id__in=selected_users):
                    user.groups.add(*group_ids)  # Corrected method
                messages.success(request, "Groups added successfully!")
            else:
                messages.error(request, "No groups provided or selected.")
        
        elif action_type == "remove_groups":  # Fixed to match the front-end action
            group_ids = request.POST.getlist("groups")
            if group_ids:
                for user in User.objects.filter(id__in=selected_users):
                    user.groups.remove(*group_ids)  # Corrected method
                messages.success(request, "Groups removed successfully!")
            else:
                messages.error(request, "No groups provided or selected.")
        
        elif action_type == "delete_users":
            userid = request.user.id
            userid = str(userid)
            if userid in selected_users:
                messages.error(request, "You cannot select your own account for deletion.")
                return redirect('user_list')  # Redirect to prevent the process from continuing
            
            users = User.objects.filter(id__in=selected_users)
            for user in users:
                if hasattr(user, 'Contact'):  # Check for associated Contact
                    user.Contact.delete()
                user.delete()
            messages.success(request, "Selected users deleted successfully!")
        
        else:
            messages.error(request, "Invalid action selected.")
        
        return redirect('staff_list')


#Logout
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')  # Redirect to login page after logout

# Login
@login_required
def login_view(request):

    form = AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # return redirect('index')
                # Get the 'next' parameter from the query string
                next_url = request.GET.get('next')
                if next_url:
                    messages.success(request, 'Logged in successfully.')
                    return redirect(next_url)  # Redirect to the page the user was trying to access
                else:
                    messages.success(request, 'Logged in successfully.')
                    return redirect('/')  # Or use a default page like 'index'
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {'form': form})



@login_required
def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if a user with this email already exists
            if User.objects.filter(username=email).exists():
                messages.error(request, 'A user with this email already exists. Please use a different email or log in.')
                return render(request, 'register.html', {'form': form})
            
            user = form.save()
            staff_group = Group.objects.get(name='Staff')
            user.groups.add(staff_group)
            messages.success(request, 'User registered successfully.')
            return redirect('login')  # Redirect to user list or any desired page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
           
    return render(request, 'register.html', {'form': form})



#Edit Users
# @login_required
# def change_password(request, user_id):
#     user = get_object_or_404(User, id=user_id)
    
#     if request.method == 'POST':
#         form = UserEditForm(request.POST, instance=user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'User has been editted successfully.')
#             return redirect('user_list')  # Redirect to a page that lists all users or any preferred page
#     else:
#         form = UserEditForm(instance=user)
#         password_form = AdminPasswordChangeForm(user=user)

#          # Customize widgets for password_form fields
#         for field_name, field in password_form.fields.items():
#             field.widget.attrs.update({
#                 'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
#                 'placeholder': f'Enter {field.label}'
#             })

#     return render(request, 'change_password.html', {
#         'form': form,
#         'password_form' : password_form, 
#         'user': user
#     })

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import AdminPasswordChangeForm
from .forms import UserEditForm  # Assuming UserEditForm is imported from your forms module
from django.contrib.auth.models import User

@login_required
def change_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Handle user edit form submission
        form = UserEditForm(request.POST, instance=user)
        
        # Handle password change form submission separately
        password_form = AdminPasswordChangeForm(user=user, data=request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'User has been edited successfully.')
        
        if password_form.is_valid():
            password_form.save()
            messages.success(request, 'Password has been updated successfully.')
            return redirect('user_list')  # Redirect to a page that lists all users or any preferred page

    else:
        # Initialize both forms for GET request
        form = UserEditForm(instance=user)
        password_form = AdminPasswordChangeForm(user=user)

        # Customize widgets for password_form fields
        for field_name, field in password_form.fields.items():
            field.widget.attrs.update({
                'class': 'w-full py-2 px-4 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300',
                'placeholder': f'Enter {field.label}'
            })

    return render(request, 'change_password.html', {
        'form': form,
        'password_form': password_form, 
        'user': user
    })
