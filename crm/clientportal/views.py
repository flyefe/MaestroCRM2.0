from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ProfileForm

@login_required
def client_portal(request):
    """Main Client Portal View"""
    profile_form = ProfileForm(instance=request.user)
    # message_form = MessageForm()

    # Handle Profile Updates
    if request.method == "POST" and 'update_profile' in request.POST:
        profile_form = ProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('client_portal')

    # Handle Message Sending
    # if request.method == "POST" and 'send_message' in request.POST:
    #     # message_form = MessageForm(request.POST)
    #     if message_form.is_valid():
    #         message = message_form.save(commit=False)
    #         message.sender = request.user
    #         message.save()
    #         messages.success(request, "Message sent successfully.")
    #         return redirect('client_portal')

    # Messages and Invoice (Placeholder)
    # user_messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'clientportal/client_portal.html', {
        'profile_form': profile_form,
        # 'message_form': message_form,
        # 'user_messages': user_messages
    })
