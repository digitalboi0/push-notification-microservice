from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class AppListView(APIView):
    def get(self, request):
        return Response({
            'success': True,
            'message': 'Apps endpoint',
            'data': []
        }, status=status.HTTP_200_OK)


class AppDetailView(APIView):
    def get(self, request, pk):
        return Response({
            'success': True,
            'message': f'App detail for {pk}',
            'data': {'id': str(pk)}
        }, status=status.HTTP_200_OK)