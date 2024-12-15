from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from django.contrib.auth.models import User, Group

from django.contrib.auth.forms import AuthenticationForm


from users.forms import RegisterForm

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

    return render(request, 'core/login.html', {'form': form})




def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if a user with this email already exists
            if User.objects.filter(username=email).exists():
                messages.error(request, 'A user with this email already exists. Please use a different email or log in.')
                return render(request, 'sign_up.html', {'form': form})
            
            user = form.save()
            staff_group = Group.objects.get(name='Contact')
            user.groups.add(staff_group)
            messages.success(request, 'User registered successfully.')
            return redirect('login')  # Redirect to user list or any desired page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
           
    return render(request, 'core/sign_up.html', {'form': form})



def permission_denied(request):
    return render(request, 'core/permission_denied.html', status=403)


@role_required(allowed_roles=['Admin', 'Manager'])
def another_view(request):
    ...


