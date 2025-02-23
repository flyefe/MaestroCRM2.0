from django.urls import path
from . import views

urlpatterns = [
    path('create-invoice', views.create_invoice, name='create_invoice'),
     path("autocomplete/contact/", views.contact_autocomplete, name="contact-autocomplete"),
]
