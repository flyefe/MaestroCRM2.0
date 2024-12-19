from django.utils.safestring import mark_safe
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from django.db.models import Count
from contacts.models import ContactDetail

@login_required
def dashboard(request):
    contacts = ContactDetail.objects.all()
    active_contacts_count = contacts.filter(status__name='Customer').count()
    unassigned_contacts_count = contacts.filter(assigned_staff__isnull=True).count()
    recent_contacts = contacts.order_by('-created_at')[:5]
    
    # In your view:
    traffic_sources = contacts.values('traffic_source__name').annotate(count=Count('traffic_source')).order_by('-count')
    traffic_sources_data = {
        'labels': [ts['traffic_source__name'] if ts['traffic_source__name'] else "Unknown" for ts in traffic_sources],
        'values': [ts['count'] for ts in traffic_sources],
    }

    traffic_sources_data = mark_safe(json.dumps(traffic_sources_data))

     # Example: Contacts grouped by month
    monthly_contacts = (
        ContactDetail.objects
        .annotate(month=TruncMonth('created_at'))  # Truncate the date to month
        .values('month')  # Group by month
        .annotate(total=Count('id'))  # Count the number of contacts per month
        .order_by('month')  # Sort by month
    )

    # Example: Traffic sources grouped by month
    monthly_traffic_sources = (
        ContactDetail.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month', 'traffic_source__name')  # Group by month and traffic_source
        .annotate(total=Count('id'))
        .order_by('month', 'traffic_source__name')
    )

    # Prepare data for chart
    mchart_labels = [item['month'].strftime('%B %Y') for item in monthly_contacts]
    mchart_data = [item['total'] for item in monthly_contacts]


    # Prepare data for the frontend
    contacts_per_month = [
        {'month': item['month'].strftime('%B %Y'), 'total': item['total']}
        for item in monthly_contacts
    ]

    traffic_sources_per_month = {}
    for item in monthly_traffic_sources:
        month = item['month'].strftime('%B %Y')
        traffic_source = item['traffic_source__name']
        total = item['total']

        if month not in traffic_sources_per_month:
            traffic_sources_per_month[month] = {}
        traffic_sources_per_month[month][traffic_source] = total



    # Services breakdown
    services_breakdown = contacts.values('services__name').annotate(count=Count('services')).order_by('-count')

    context = {
        'contacts': contacts,
        'active_contacts_count': active_contacts_count,
        'unassigned_contacts_count': unassigned_contacts_count,
        'recent_contacts': recent_contacts,
        'traffic_sources_data': traffic_sources_data,
        'contacts_per_month': contacts_per_month,
        'mchart_labels': mchart_labels,
        'mchart_data': mchart_data,

        'traffic_sources_per_month': traffic_sources_per_month,
        'services_breakdown': {service['services__name']: service['count'] for service in services_breakdown},
    }
    return render(request, 'dashboard/dashboard.html', context)
