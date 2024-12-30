from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Contact
from .serializers import ContactSerializer

class CreateContactAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save(created_by=request.user, updated_by=request.user)
            return Response({
                "message": "Contact created successfully.",
                "contact": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
