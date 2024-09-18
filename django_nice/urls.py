from django.urls import path
from .sse import sse_manager
from .views import ModelAPI

def register_endpoints(app_label, model_name, field_name, object_id):
    """
    Register the API and SSE endpoints for the project.
    """
    return [
        # API endpoint for getting a specific field value from a model instance
        path(f'api/{app_label}/{model_name}/{object_id}/', ModelAPI.as_view(), name=f'{model_name}_detail'),

        # SSE endpoint for streaming updates of the field in a model instance
        path(f'api/sse/{app_label}/{model_name}/{field_name}/', sse_manager.stream_updates, name=f'{model_name}_sse'),
    ]