from django.urls import path
from .views import ModelAPI, sse_manager

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            # Default values for the configuration
            cls._instance.host = 'http://127.0.0.1:8000'
            cls._instance.api_endpoint = '/api'
        return cls._instance

    @classmethod
    def configure(cls, host, api_endpoint='/api'):
        """
        Configure the base URL (host) and API endpoint for the library.
        """
        config = cls._instance or cls()
        config.host = host.rstrip('/')  
        config.api_endpoint = api_endpoint.rstrip('/') 

    @classmethod
    def get_host(cls):
        return cls._instance.host

    @classmethod
    def get_api_endpoint(cls):
        return cls._instance.api_endpoint

    @classmethod
    def add_urls_to_project(cls, urlpatterns, app_label, model_name, field_name, object_id):
        """
        Add API and SSE endpoints for the model.
        """
        urlpatterns += [
            # API endpoint to get or update the model's data
            path(f'api/{app_label}/{model_name}/<int:object_id>/<str:field_name>/', 
                 ModelAPI.as_view(), name=f'{model_name}_detail'),

            # SSE endpoint to stream updates of a specific field
            path(f'api/sse/{app_label}/{model_name}/{field_name}/', 
                 sse_manager.stream_updates, name=f'{model_name}_sse'),
        ]