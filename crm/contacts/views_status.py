from django.shortcuts import render, redirect, get_object_or_404
from .models import Status
from .forms import StatusForm

from django.contrib.auth.decorators import login_required

from core.decorators import role_required


# View to create a new Status
@login_required
def status_list(request):
    statuses = Status.objects.all()  # Fetch all statuses for display

    if request.method == 'POST':
        form = StatusForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('status_list')  # Redirect to status list view
    else:
        form = StatusForm()  # Provide an empty form for GET requests

    # Render the form and statuses
    return render(request, 'status/status_list.html', {
        'form': form,
        'statuses': statuses
    })


# View to update an existing Status
@role_required(['Admin'])
@login_required
def edit_status(request, status_id):
    # Fetch the status object or return a 404 if not found
    status = get_object_or_404(Status, id=status_id)

    if request.method == 'POST':
        form = StatusForm(request.POST, instance=status)  # Bind form to the existing status
        if form.is_valid():
            form.save()  # Save the updates to the database
            return redirect('status_list')  # Redirect to status list view
    else:
        form = StatusForm(instance=status)  # Prepopulate form with current status data

    # Render the form for updating
    return render(request, 'status/edit_status.html', {
        'form': form,
        'is_update': True,  # Optional flag to indicate update mode in the template
        'status': status
    })

# View to delete an existing Status
@role_required(['Admin'])
@login_required
def delete_status(request, status_id):
    status = get_object_or_404(Status, id=status_id)  # Fetch status object

    if request.method == 'POST':
        status.delete()  # Delete the status from the database
        return redirect('status_list')  # Redirect to status list view

    # Confirm deletion with a simple template
    return render(request, 'status_confirm_delete.html', {
        'status': status
    })
