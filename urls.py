from django.urls import path
from .views import ModelUpdateAPIView
from .sse import sse_manager

def register_endpoints(app_label, model_name):
    """
    Function to register the API and SSE endpoints for a specific model.
    """
    return [
        path(f'{app_label}/{model_name}/<int:pk>/', ModelUpdateAPIView.as_view(), name=f'{model_name}_update'),
        path(f'{app_label}/{model_name}/<int:pk>/<str:field_name>/', ModelUpdateAPIView.as_view(), name=f'{model_name}_field_update'),
        path(f'sse/{app_label}/{model_name}/<str:field_name>/', sse_manager.stream_updates, name=f'{model_name}_sse'),
    ]
