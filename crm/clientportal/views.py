from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from contacts.models import ContactDetail
from contacts.forms import ContactDetailCreationForm # Assuming this form is defined elsewhere

@login_required
def client_portal(request):
    """Main Client Portal View"""
    # Fetch or create the user's ContactDetail
    try:
        contact_detail = ContactDetail.objects.get(user=request.user)
    except ContactDetail.DoesNotExist:
        # If no ContactDetail exists, create one
        contact_detail = ContactDetail(user=request.user)
        contact_detail.save()

    # Initialize the form with the existing contact detail
    contact_detail_form = ContactDetailCreationForm(instance=contact_detail)

    # Handle Profile (Contact Detail) Updates
    if request.method == "POST" and 'update_profile' in request.POST:
        contact_detail_form = ContactDetailCreationForm(request.POST, instance=contact_detail)
        if contact_detail_form.is_valid():
            contact_detail_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('client_portal')

    # Placeholder for messages (replace with actual implementation when ready)
    # messages = []
    # invoices = []

    # Render the client portal page with form
    return render(request, 'clientportal/client_portal.html', {
        'form': contact_detail_form,
        # 'messages': messages,
        # 'invoices': invoices
    })