from django.shortcuts import redirect
# from django.contrib.auth.models import User, Group

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and not request.user.groups.filter(name='Admin').exists():
            return redirect('permission_denied')
        if request.path.startswith('/contacts/') and not request.user.groups.filter(name__in=['Admin', 'Staff']).exists():
            return redirect('permission_denied')
        if request.path.startswith('/client-portal/') and not request.user.groups.filter(name='Contacts').exists():
            return redirect('permission_denied')

        return self.get_response(request)
