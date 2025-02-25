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

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Invoice, InvoiceItem, ExchangeRate, BusinessSettings, Contact
from django.contrib import messages

@csrf_exempt  # Remove if using CSRF token in frontend
def create_invoice(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON request from frontend

            # Extract Invoice Data
            business_id = data.get("business_settings_id")
            assign_to_id = data.get("assign_to_id")
            due_date = data.get("due_date")
            unit_measurement = data.get("unit_measurement")
            quote_currency = data.get("quote_currency")
            subtotal = float(data.get("subtotal", 0))
            total_vat = float(data.get("total_vat", 0))
            grand_total = float(data.get("grand_total", 0))
            status = data.get("status")

            # Retrieve BusinessSettings and Contact
            business_settings = get_object_or_404(BusinessSettings, id=business_id)
            assign_to = get_object_or_404(Contact, id=assign_to_id)

            # Create Invoice
            invoice = Invoice.objects.create(
                business_settings=business_settings,
                Assign_to=assign_to,
                due_date=due_date,
                unit_measurement=unit_measurement,
                quote_currency=quote_currency,
                subtotal=subtotal,
                total_vat=total_vat,
                grand_total=grand_total,
                status=status,
                created_by=request.user if request.user.is_authenticated else None
            )

            # Extract Invoice Items
            items = data.get("items", [])
            for item in items:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    title=item.get("title"),
                    description=item.get("description"),
                    unit_measurement=item.get("unit_measurement"),
                    unit=float(item.get("unit", 1)),
                    price=float(item.get("price", 0)),
                    currency=item.get("currency"),
                    quote_currency_equivalent=float(item.get("quote_currency_equivalent", 0)),
                    tax_percentage=float(item.get("tax_percentage", 0)),
                    amount=float(item.get("amount", 0))
                )

            # Extract Exchange Rate
            exchange_rates = data.get("exchange_rates", [])
            for rate in exchange_rates:
                ExchangeRate.objects.update_or_create(
                    base_currency=rate.get("base_currency"),
                    target_currency=rate.get("target_currency"),
                    defaults={"rate": float(rate.get("rate", 1))}
                )

            return JsonResponse({"message": "Invoice created successfully!", "invoice_id": invoice.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
    business_name = 'G-Line Logistics'
    business_type = 'Shipment'
    contact_email = 'example@email.com'
    website_link = 'www.g-linelogistics.com'
    company_logo_url = config('COMPANY_LOGO_URL')

    # Extract Invoice Data
    business_id = data.get("business_settings_id")
    assign_to_id = data.get("assign_to_id")
    due_date = data.get("due_date")
    unit_measurement = data.get("unit_measurement")
    quote_currency = data.get("quote_currency")
    subtotal = float(data.get("subtotal", 0))
    total_vat = float(data.get("total_vat", 0))
    grand_total = float(data.get("grand_total", 0))
    status = data.get("status")

    # Retrieve BusinessSettings and Contact
    business_settings = get_object_or_404(BusinessSettings, id=business_id)
    assign_to = get_object_or_404(Contact, id=assign_to_id)

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

    # return JsonResponse({"error": "Invalid request method"}, status=405)

