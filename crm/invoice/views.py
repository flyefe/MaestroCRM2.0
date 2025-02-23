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

from core.decorators import role_required

# Create your views here.
@login_required
def create_invoice(request):
    return render(request, 'invoice/create_invoice.html')