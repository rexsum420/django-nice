from django.http import StreamingHttpResponse
from collections import deque
import time

class SSEManager:
    _listeners = {}

    @classmethod
    def register_listener(cls, model_name, object_id, field_name):
        if model_name not in cls._listeners:
            cls._listeners[model_name] = {}
        if object_id not in cls._listeners[model_name]:
            cls._listeners[model_name][object_id] = {}
        if field_name not in cls._listeners[model_name][object_id]:
            cls._listeners[model_name][object_id][field_name] = deque() 
        return cls._listeners[model_name][object_id][field_name]

    @classmethod
    def notify_listeners(cls, model_name, object_id, field_name, new_value):
        listeners = cls._listeners.get(model_name, {}).get(object_id, {}).get(field_name, deque())
        listeners.append(new_value)

    @classmethod
    def stream_updates(cls, request, app_label, model_name, object_id, field_name):
        def event_stream():
            listeners = cls.register_listener(model_name, object_id, field_name)

            from django.apps import apps
            model = apps.get_model(app_label, model_name)
            try:
                instance = model.objects.get(pk=object_id)
                last_value = getattr(instance, field_name)
            except model.DoesNotExist:
                last_value = None

            if last_value is not None:
                yield f"data: {last_value}\n\n"

            try:
                while True:
                    if listeners:
                        try:
                            new_value = listeners.popleft() 
                            yield f"data: {new_value}\n\n"
                        except IndexError:
                            pass 
                    yield ":\n\n"
                    time.sleep(1)
            except GeneratorExit:
                cls._listeners[model_name][object_id][field_name].clear()
                raise

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
