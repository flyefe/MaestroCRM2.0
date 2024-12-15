from django.urls import path
from .views import index, about, sign_up, login_view, logout_view, permission_denied



urlpatterns = [
     #Public-facing URl
    path("index", index, name='index'),
    path("about/", about, name='about'),
    path("permission-denied/", permission_denied, name='permission_denied'),
    path("login/", login_view, name='login'),
    path('sign-up/', sign_up, name='sign_up'),
    path("logout/", logout_view, name='logout'),
]