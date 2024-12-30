from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from django.contrib import messages
from contacts.models import Contact
from contacts.forms import ContactCreationForm # Assuming this form is defined elsewhere

@login_required
def client_portal(request):
    """Main Client Portal View"""

    # Fetch or create the user's Contact
    try:
        contact = Contact.objects.get(user=request.user)
    except Contact.DoesNotExist:
        # If no Contact exists, create one with default values
        contact = Contact(user=request.user)
        contact.save()

    # Handle Profile (Contact Detail) Updates
    if request.method == "POST" and 'update_profile' in request.POST:
        form = ContactCreationForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('client_portal')
    else:
        # Populate the form with current contact details
        form_initial = {
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'tag': ', '.join(contact.tags.values_list('name', flat=True)),
        }
        # Include user details if they exist
        if contact.user:
            form_initial.update({
                'email': contact.user.email,
                'first_name': contact.user.first_name,
                'last_name': contact.user.last_name,
            })

        form = ContactCreationForm(instance=contact, initial=form_initial)

    context = {
        'form': form,
    }

    # Render the client portal page with form
    return render(request, 'clientportal/client_portal.html', context)
