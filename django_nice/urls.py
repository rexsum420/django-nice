from django.urls import path
from .views import ModelAPI
from .sse import SSEManager


def register_endpoints(app_label, model_name, api_endpoint):
    return [
        path(
            f'{api_endpoint}/<str:app_label>/<str:model_name>/<int:object_id>/<str:field_name>/',
            ModelAPI.as_view(),
            name=f'{model_name}_detail'
        ),
        path(
            f'{api_endpoint}/sse/<str:app_label>/<str:model_name>/<int:object_id>/<str:field_name>/',
            lambda request, app_label, model_name, object_id, field_name:
            SSEManager.stream_updates(request, app_label, model_name, object_id, field_name),
            name=f'{model_name}_sse'
        ),
    ]
