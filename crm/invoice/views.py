from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from django.contrib.auth.models import User, Group

from settings.models import TrafficSource, Service, Status


from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib import messages
from contacts.models import Contact

from .forms import InvoiceForm
from users.forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm

from emails.email_utils import send_custom_email

from core.decorators import role_required

# Create your views here.



def contact_autocomplete(request):
    query = request.GET.get("query", "")
    results = []

    if query:
        contacts = Contact.objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        )[:10]  # Limit results to 10

        results = [
            {"id": contact.id, "name": contact.name, "email": contact.email} for contact in contacts
        ]

    return JsonResponse({"results": results})

@login_required
def create_invoice(request):

    business_name = 'G-Line Logistics'
    business_type = 'Shipment'
    contact_email = 'example@email.com'
    website_link = 'www.g-linelogistics.com'
    form = InvoiceForm()  # Instantiate the form

 
    context = {
        'business_name': business_name,
        'business_type' : business_type,
        'contact_email' : contact_email,
        'website_link' : website_link,
        'form' : form,

    }
    return render(request, 'invoice/create_invoice.html', context=context)