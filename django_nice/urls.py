from django.urls import path
from .views import ModelAPI, AuthModelAPI
from .sse import SSEManager

def register_endpoints(app_label, model_name, api_endpoint, require_auth):
    view = ModelAPI.as_view()
    if require_auth:
        view = AuthModelAPI.as_view()

    return [
        path(
            f'{api_endpoint}/<str:app_label>/<str:model_name>/<int:object_id>/<str:field_name>/',
            view,
            name=f'{model_name}_detail'
        ),
        path(
            f'{api_endpoint}/sse/<str:app_label>/<str:model_name>/<int:object_id>/<str:field_name>/',
            lambda request, app_label, model_name, object_id, field_name:
            SSEManager.stream_updates(request, app_label, model_name, object_id, field_name),
            name=f'{model_name}_sse'
        ),
    ]
