from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from emails.utils import send_email
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

# @login_required
# def create_invoice(request):

#     business_name = 'G-Line Logistics'
#     business_type = 'Shipment'
#     contact_email = 'example@email.com'
#     website_link = 'www.g-linelogistics.com'
#     company_logo_url = config('COMPANY_LOGO_URL')

#     context = {
#         'unit_measurement_choices': InvoiceItem.UNIT_MEASUREMENT_CHOICES,
#         'currency_choices': InvoiceItem.CURRENCY_CHOICES,
#         'quote_currency_choices': Invoice.QUOTE_CURRENCY_CHOICES,
#         'status_choices': Invoice.STATUS_CHOICES,
#         'business_name': business_name,
#         'business_type': business_type,
#         'contact_email': contact_email,
#         'website_link': website_link,
#         'company_logo_url' : company_logo_url
#     }
#     return render(request, 'invoice/create_invoice.html', context=context)


from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from decouple import config
import json

from contacts.models import Contact
# from .models import Invoice, InvoiceItem
from . import models

@login_required
def create_invoice(request):
    """Handles rendering the invoice creation page and processing AJAX form submission."""
    
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            # Retrieve form data
            invoice_status = request.POST.get("invoice_status")
            invoice_date = request.POST.get("invoice_date")
            reference_number = request.POST.get("reference_number")
            due_date = request.POST.get("due_date")
            unit_measurement = request.POST.get("unit_measurement")
            quote_currency = request.POST.get("quote_currency")
            rate_naira_usd = request.POST.get("rate_naira_usd", 0)
            rate_yuan_usd = request.POST.get("rate_yuan_usd", 0)
            rate_naira_yuan = request.POST.get("rate_naira_yuan", 0)
            assign_to = request.POST.get("contact")  # Expected to be the contact ID
            items_data = json.loads(request.POST.get("items", "[]"))

            # Fetch contact by ID
            contact = Contact.objects.get(id=assign_to)

            # Create invoice
            invoice = Invoice.objects.create(
                contact=contact,
                invoice_status=invoice_status,
                invoice_date=invoice_date,
                reference_number=reference_number,
                due_date=due_date,
                unit_measurement=unit_measurement,
                quote_currency=quote_currency,
                rate_naira_usd=rate_naira_usd,
                rate_yuan_usd=rate_yuan_usd,
                rate_naira_yuan=rate_naira_yuan
            )

            # Add invoice items
            for item in items_data:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    title=item["title"],
                    description=item["description"],
                    unit=item["unit"],
                    price=item["price"],
                    currency=item["currency"],
                    tax=item["tax"]
                )

            return JsonResponse({"success": True, "message": "Invoice created!", "redirect_url": "/invoices/"})

        except Contact.DoesNotExist:
            return JsonResponse({"success": False, "message": "Selected contact does not exist."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    # Data for rendering the template
    context = {
        # 'unit_measurement_choices': UNIT_MEASUREMENT_CHOICES,
        # 'currency_choices': CURRENCY_CHOICES,
        # 'quote_currency_choices': QUOTE_CURRENCY_CHOICES,
        # 'status_choices': STATUS_CHOICES,
        'unit_measurement_choices': InvoiceItem._meta.get_field('unit_measurement').choices,
        'currency_choices': InvoiceItem._meta.get_field('currency').choices,
        'quote_currency_choices': Invoice._meta.get_field('quote_currency').choices,
        'status_choices': Invoice._meta.get_field('status').choices,
        'business_name': 'G-Line Logistics',
        'business_type': 'Shipment',
        'contact_email': 'example@email.com',
        'website_link': 'www.g-linelogistics.com',
        'company_logo_url': config('COMPANY_LOGO_URL')
    }
    
    return render(request, 'invoice/create_invoice.html', context=context)
