from django.http import StreamingHttpResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

class SSEManager:
    """
    A class to manage SSE updates for any model and field.
    """

    def __init__(self):
        self.listeners = {}

    def register_model(self, app_label, model_name, field_name):
        """
        Register a model for SSE updates when a specific field changes.
        """
        model = apps.get_model(app_label, model_name)

        @receiver(post_save, sender=model)
        def model_update_handler(sender, instance, **kwargs):
            if field_name in instance.get_dirty_fields():
                new_value = getattr(instance, field_name)
                if model_name in self.listeners:
                    for listener in self.listeners[model_name]:
                        listener(new_value)

    def add_listener(self, model_name, listener):
        """
        Add a listener for a model. The listener will be called when an SSE event occurs.
        """
        if model_name not in self.listeners:
            self.listeners[model_name] = []
        self.listeners[model_name].append(listener)

    def stream_updates(self, request, app_label, model_name, field_name):
        """
        Stream updates via Server-Sent Events (SSE) for a specific model field.
        """
        def event_stream():
            model = apps.get_model(app_label, model_name)
            last_value = None

            # Get the first instance of the model (or adjust this to meet your requirements)
            instance = model.objects.first()
            if instance:
                last_value = getattr(instance, field_name)
                yield f"data: {last_value}\n\n"

            while True:
                # Continuously check for changes
                new_value = getattr(model.objects.first(), field_name, None)
                if new_value != last_value:
                    last_value = new_value
                    yield f"data: {new_value}\n\n"
        
        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

# Singleton instance of SSEManager
sse_manager = SSEManager()
