from django.urls import path
from .views.notification_views import SendNotificationView, BulkSendNotificationView
from .views.app_views import AppListView, AppDetailView
from .views.device_views import DeviceRegistrationView
from .views.template_views import TemplateListView, TemplateDetailView, TemplatePreviewView

urlpatterns = [
    path('notifications/send/', SendNotificationView.as_view(), name='send-notification'),
    path('notifications/bulk/', BulkSendNotificationView.as_view(), name='bulk-send-notification'),
    path('apps/', AppListView.as_view(), name='app-list'),
    path('apps/<uuid:pk>/', AppDetailView.as_view(), name='app-detail'),
    path('devices/register/', DeviceRegistrationView.as_view(), name='device-register'),
    path('templates/', TemplateListView.as_view(), name='template-list'),
    path('templates/<uuid:pk>/', TemplateDetailView.as_view(), name='template-detail'),
    path('templates/preview/', TemplatePreviewView.as_view(), name='template-preview'),
]