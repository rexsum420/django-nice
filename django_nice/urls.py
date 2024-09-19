from django.urls import path
from .views import ModelAPI
from .sse import SSEManager

def register_endpoints(app_label, model_name, field_name, object_id, api_endpoint):
    return [
        path(
            f'{api_endpoint}/<app_label>/<model_name>/<object_id>/<field_name>/', 
            ModelAPI.as_view(),
            name=f'{model_name}_detail'
        ),
        path(
            f'{api_endpoint}/sse/{app_label}/{model_name}/{object_id}/{field_name}/',
            lambda request, app_label=app_label, model_name=model_name, field_name=field_name:
            SSEManager.stream_updates(request, app_label, model_name, object_id, field_name),
            name=f'{model_name}_sse'
        ),
    ]
