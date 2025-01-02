from django.shortcuts import render, redirect, get_object_or_404
from .models import TrafficSource
from .forms import TrafficSourceForm

from django.contrib.auth.decorators import login_required

from core.decorators import role_required

# View to create a new TrafficSource
# @role_required(['Admin'])
@login_required
def traffic_source_list(request):
    traffic_sources = TrafficSource.objects.all()  # Fetch all traffic_sources for display

    if request.method == 'POST':
        form = TrafficSourceForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('traffic_source_list')  # Redirect to traffic_source list view
    else:
        form = TrafficSourceForm()  # Provide an empty form for GET requests

    # Render the form and traffic_sources
    return render(request, 'setting/trafficsource/traffic_source_list.html', {
        'form': form,
        'traffic_sources': traffic_sources
    })


# View to update an existing TrafficSource
@role_required(['Admin'])
@login_required
def edit_traffic_source(request, traffic_source_id):
    # Fetch the traffic_source object or return a 404 if not found
    traffic_source = get_object_or_404(TrafficSource, id=traffic_source_id)

    if request.method == 'POST':
        form = TrafficSourceForm(request.POST, instance=traffic_source)  # Bind form to the existing traffic_source
        if form.is_valid():
            form.save()  # Save the updates to the database
            return redirect('traffic_source_list')  # Redirect to traffic_source list view
    else:
        form = TrafficSourceForm(instance=traffic_source)  # Prepopulate form with current traffic_source data

    # Render the form for updating
    return render(request, 'setting/trafficsource/edit_traffic_source.html', {
        'form': form,
        'is_update': True,  # Optional flag to indicate update mode in the template
        'traffic_source': traffic_source
    })

# View to delete an existing TrafficSource
@role_required(['Admin'])
@login_required
def delete_traffic_source(request, traffic_source_id):
    traffic_source = get_object_or_404(TrafficSource, id=traffic_source_id)  # Fetch traffic_source object

    if request.method == 'POST':
        traffic_source.delete()  # Delete the traffic_source from the database
        return redirect('traffic_source_list')  # Redirect to traffic_source list view

    # Confirm deletion with a simple template
    return render(request, 'traffic_source_confirm_delete.html', {
        'traffic_source': traffic_source
    })
