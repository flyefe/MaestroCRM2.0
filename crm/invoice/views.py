from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from emails.email_utils import send_custom_email
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User, Group
from settings.models import TrafficSource, Service
from contacts.models import Contact
from .models import Invoice, InvoiceItem, InvoiceTag
import logging

from decouple import config

logger = logging.getLogger(__name__)




@csrf_exempt
def contact_autocomplete(request):
    query = request.GET.get("query", "")
    # logger.info(f"Received query: {query}")  # Log query to check if it's being received
    results = []

    if query:
        contacts = Contact.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(middle_name__icontains=query) |
            Q(email__icontains=query)
        )[:10]  # Limit results to 10

        results = [
            {
                "id": contact.id,
                "name": f"{contact.first_name} {contact.middle_name} {contact.last_name}".strip(),
                "email": contact.email
            }
            for contact in contacts
        ]

    return JsonResponse({"results": results})

@login_required
def create_invoice(request):

    business_name = 'G-Line Logistics'
    business_type = 'Shipment'
    contact_email = 'example@email.com'
    website_link = 'www.g-linelogistics.com'
    company_logo_url = config('COMPANY_LOGO_URL')

    context = {
        'unit_measurement_choices': InvoiceItem.UNIT_MEASUREMENT_CHOICES,
        'currency_choices': InvoiceItem.CURRENCY_CHOICES,
        'quote_currency_choices': Invoice.QUOTE_CURRENCY_CHOICES,
        'status_choices': Invoice.STATUS_CHOICES,
        'business_name': business_name,
        'business_type': business_type,
        'contact_email': contact_email,
        'website_link': website_link,
        'company_logo_url' : company_logo_url
    }
    return render(request, 'invoice/create_invoice.html', context=context)
