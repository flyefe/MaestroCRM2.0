from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['first_name', 'middle_name', 'last_name', 'email', 'phone_number', 
                  'traffic_source', 'services', 'referred_by']
        
        def validate(self, data):
            if not data.get('first_name') and not data.get('email'):
                raise serializers.ValidationError("Either first_name or email is required.")
            return data
