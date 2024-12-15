from django.shortcuts import redirect

def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')  # Redirect unauthenticated users to login
            user_roles = request.user.groups.values_list('name', flat=True)
            if not any(role in user_roles for role in allowed_roles):
                return redirect('permission_denied')  # Redirect if user doesn't have the required role
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator



