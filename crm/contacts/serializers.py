from rest_framework import serializers
from .models import Contact, TrafficSource

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'traffic_source']
        extra_kwargs = {
            'email': {'required': True},
            'phone_number': {'required': True},
        }
