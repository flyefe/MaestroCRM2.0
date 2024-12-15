from django.contrib.auth.models import Group

def user_roles(request):
    if request.user.is_authenticated:
        groups = request.user.groups.values_list('name', flat=True)
        return {'user_roles': groups}
    return {}
