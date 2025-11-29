from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class DeviceRegistrationView(APIView):
    def post(self, request):
        return Response({
            'success': True,
            'message': 'Device registration endpoint',
            'data': None
        }, status=status.HTTP_201_CREATED)