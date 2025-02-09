from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from django.contrib.auth.models import User, Group

from settings.models import TrafficSource, Service, Status

from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib import messages
from contacts.models import Contact

from users.forms import SignUpForm
from emails.email_utils import send_custom_email

from .decorators import role_required


@login_required
def index(request):
    return render(request, 'core/index.html')

@login_required
def about(request):
    return render(request, 'core/about.html')

#Logout
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')  # Redirect to login page after logout

# Login
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
                #Send a login email
                # Send welcome email
                # send_custom_email(
                #     subject="Welcome Back. You logged in",
                #     recipient_list=[user.email],
                #     template_name="emails/registration_email.html",
                #     context={"user": user},
                # )
                # Get the 'next' parameter from the query string
                next_url = request.GET.get('next')
                if next_url:
                    messages.success(request, 'Logged in successfully.')
                    return redirect(next_url)  # Redirect to the page the user was trying to access
                else:
                    messages.success(request, 'Logged in successfully.')
                    # Check if user is in Staff or Admin group
                    if user.groups.filter(name__in=['Staff', 'Admin']).exists():
                        return redirect('my_assigned_contacts')  # Or use a default page like 'index'
                    else:
                        return redirect('client_portal')

            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'core/login.html', {'form': form})




def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Validate email domain
            if not email.endswith('@flyibat.com'):
                messages.error(
                    request,
                    "You are not a staff. contact a staff memeber to get access to your client portal"
                )
                return render(request, 'core/sign_up.html', {'form': form})
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password']

            # Check if a user with this email already exists
            if User.objects.filter(username=email).exists():
                messages.error(
                    request,
                    'A user with this email already exists. Please use a different email or log in.'
                )
                return render(request, 'core/sign_up.html', {'form': form})

            # Save the user
            user = form.save(commit=False)
            user.username = email
            user.last_name = last_name if first_name else 'last name not present'
            user.first_name = first_name if first_name else 'first name not present'
            user.set_password(password)
            user.save()
            print(f"First Name: {first_name}, Last Name: {last_name}")

            # If the user is the first user, perform initial setup
            if user.id == 1:
                # Create roles
                admin_group, _ = Group.objects.get_or_create(name='Admin')
                staff_group, _ = Group.objects.get_or_create(name='Staff')
                contact_group, _ = Group.objects.get_or_create(name='Contact')

                # Grant admin permissions to the Admin group
                user.groups.add(admin_group)

                # Create traffic sources
                traffic_sources = [
                    'Facebook', 'Instagram', 'X', 'Google', 'Walk-in', 'Others'
                ]
                for source in traffic_sources:
                    TrafficSource.objects.get_or_create(name=source)

                # Create basic services
                basic_services = ['Service 1', 'Service 2']
                for service in basic_services:
                    Service.objects.get_or_create(name=service)

                # Create basic statuses
                statuses = ['Lead', 'Prospect', 'Customer', 'Closed']
                for status in statuses:
                    Status.objects.get_or_create(name=status)

            else:
                # Assign the user to the Contact group
                contact_group = Group.objects.get(name='Contact')
                user.groups.add(contact_group)

                # Create contact details for the user
                contact = Contact.objects.create(user=user)

                # Assign the contact to the 'Lead' status
                lead_status = Status.objects.get(name='Lead')
                contact.status = lead_status
                contact.save()

            # Send welcome email
            send_custom_email(
                subject="Welcome to Our System",
                recipient_list=[user.email],
                template_name="emails/registration_email.html",
                context={"user": user},
            )
            messages.success(request, 'User registered successfully.')
            return redirect(
                'login')  # Redirect to the login page or desired page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()

    return render(request, 'core/sign_up.html', {'form': form})




def permission_denied(request):
    return render(request, 'core/permission_denied.html', status=403)


@role_required(allowed_roles=['Admin', 'Manager'])
def another_view(request):
    ...
