from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class TemplateListView(APIView):
    def get(self, request):
        return Response({
            'success': True,
            'message': 'Templates endpoint',
            'data': []
        }, status=status.HTTP_200_OK)


class TemplateDetailView(APIView):
    def get(self, request, pk):
        return Response({
            'success': True,
            'message': f'Template detail for {pk}',
            'data': {'id': str(pk)}
        }, status=status.HTTP_200_OK)


class TemplatePreviewView(APIView):
    def post(self, request):
        return Response({
            'success': True,
            'message': 'Template preview endpoint',
            'data': None
        }, status=status.HTTP_200_OK)