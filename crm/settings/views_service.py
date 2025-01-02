from django.shortcuts import render, redirect, get_object_or_404
from .models import Service
from .forms import ServiceForm

from django.contrib.auth.decorators import login_required
from core.decorators import role_required


# View to create a new Service

@login_required
def service_list(request):
    services = Service.objects.all()  # Fetch all services for display

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('service_list')  # Redirect to service list view
    else:
        form = ServiceForm()  # Provide an empty form for GET requests

    # Render the form and services
    return render(request, 'setting/service/service_list.html', {
        'form': form,
        'services': services
    })


# View to update an existing Service
@role_required(['Admin'])
@login_required
def edit_service(request, service_id):
    # Fetch the service object or return a 404 if not found
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)  # Bind form to the existing service
        if form.is_valid():
            form.save()  # Save the updates to the database
            return redirect('service_list')  # Redirect to service list view
    else:
        form = ServiceForm(instance=service)  # Prepopulate form with current service data

    # Render the form for updating
    return render(request, 'setting/service/edit_service.html', {
        'form': form,
        'is_update': True,  # Optional flag to indicate update mode in the template
        'service': service
    })

# View to delete an existing Service
@role_required(['Admin'])
@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)  # Fetch service object

    if request.method == 'POST':
        service.delete()  # Delete the service from the database
        return redirect('service_list')  # Redirect to service list view

    # Confirm deletion with a simple template
    return render(request, 'service_confirm_delete.html', {
        'service': service
    })
