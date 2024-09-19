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
            cls._listeners[model_name][object_id][field_name] = deque()  # Using a deque as the update queue
        return cls._listeners[model_name][object_id][field_name]

    @classmethod
    def notify_listeners(cls, model_name, object_id, field_name, new_value):
        listeners = cls._listeners.get(model_name, {}).get(object_id, {}).get(field_name, deque())
        print(f"Notifying {len(listeners)} listeners for {model_name} {object_id} {field_name} with new value {new_value}")
        listeners.append(new_value)  # Append the new value to the deque for all listeners

    @classmethod
    def stream_updates(cls, request, app_label, model_name, object_id, field_name):
        # Event stream function to yield events to the client
        def event_stream():
            listeners = cls.register_listener(model_name, object_id, field_name)

            from django.apps import apps
            model = apps.get_model(app_label, model_name)
            try:
                instance = model.objects.get(pk=object_id)
                last_value = getattr(instance, field_name)
            except model.DoesNotExist:
                last_value = None

            # Send the initial value if it exists
            if last_value is not None:
                yield f"data: {last_value}\n\n"

            # Continuously yield updates from the deque
            try:
                while True:
                    if listeners:
                        try:
                            new_value = listeners.popleft()  # Fetch the new value
                            
                            print(f"Sending SSE update: {new_value}")
                            yield f"data: {new_value}\n\n"
                        except IndexError:
                            pass  # No update available, keep the connection open
                    yield ":\n\n"  # Send keep-alive to prevent timeout
                    time.sleep(1)  # Avoid busy waiting
            except GeneratorExit:
                # Client disconnected, clear the deque
                print(f"Removing listener for {model_name} {object_id} {field_name}")
                cls._listeners[model_name][object_id][field_name].clear()
                raise

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
