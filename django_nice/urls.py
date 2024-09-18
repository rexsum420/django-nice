from django.urls import path
from .views import ModelAPI
from .sse import sse_manager

def register_endpoints(app_label, model_name, field_name, object_id):
    """
    Register the API and SSE endpoints for the project.
    """
    return [
        # API endpoint for getting a specific field value from a model instance
        path(f'api/{app_label}/{model_name}/<int:object_id>/<str:field_name>/', 
             ModelAPI.as_view(), name=f'{model_name}_detail'),

        # SSE endpoint for streaming updates of the field in a model instance
        path(f'api/sse/{app_label}/{model_name}/{field_name}/', 
             sse_manager.stream_updates(app_label=app_label, model_name=model_name, field_name=field_name), name=f'{model_name}_sse'),
    ]