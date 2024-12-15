from django.shortcuts import render, redirect
from .forms import UpdateSettingsForm
from .models import Status, Service, TrafficSource

def update_settings(request):
    if request.method == 'POST':
        form = UpdateSettingsForm(request.POST)
        if form.is_valid():
            # Clear all previous data
            Status.objects.all().delete()
            Service.objects.all().delete()
            TrafficSource.objects.all().delete()

            # Process and add new Statuses
            statuses = form.cleaned_data['statuses']
            if statuses:
                status_names = {name.strip().title() for name in statuses.split(',') if name.strip()}
                for name in status_names:
                    Status.objects.create(name=name)

            # Process and add new Services
            services = form.cleaned_data['services']
            if services:
                service_names = {name.strip().title() for name in services.split(',') if name.strip()}
                for name in service_names:
                    Service.objects.create(name=name)

            # Process and add new Traffic Sources
            traffic_sources = form.cleaned_data['traffic_sources']
            if traffic_sources:
                traffic_source_names = {name.strip().title() for name in traffic_sources.split(',') if name.strip()}
                for name in traffic_source_names:
                    TrafficSource.objects.create(name=name)

            return redirect('contact_list')  # Redirect to the desired page
    else:
        # Query existing values for editing
        existing_statuses = ', '.join(Status.objects.values_list('name', flat=True))
        existing_services = ', '.join(Service.objects.values_list('name', flat=True))
        existing_traffic_sources = ', '.join(TrafficSource.objects.values_list('name', flat=True))

        # Prepopulate the form with existing data
        form = UpdateSettingsForm(initial={
            'statuses': existing_statuses,
            'services': existing_services,
            'traffic_sources': existing_traffic_sources,
        })

    return render(request, 'setting/update_settings.html', {'form': form})


