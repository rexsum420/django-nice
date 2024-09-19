from django.http import StreamingHttpResponse

class SSEManager:
    _listeners = {}

    @classmethod
    def register_listener(cls, model_name, object_id, field_name):
        if model_name not in cls._listeners:
            cls._listeners[model_name] = {}
        if object_id not in cls._listeners[model_name]:
            cls._listeners[model_name][object_id] = {}
        if field_name not in cls._listeners[model_name][object_id]:
            cls._listeners[model_name][object_id][field_name] = []
        return cls._listeners[model_name][object_id][field_name]

    @classmethod
    def notify_listeners(cls, model_name, object_id, field_name, new_value):
        listeners = cls._listeners.get(model_name, {}).get(object_id, {}).get(field_name, [])
        for listener in listeners:
            listener(new_value)

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

            def send_update(new_value):
                nonlocal last_value
                if new_value != last_value:
                    last_value = new_value
                    yield f"data: {new_value}\n\n"

            listeners.append(lambda new_value: send_update(new_value))

            yield from send_update(last_value)

            try:
                while True:
                    if request.META.get('HTTP_CONNECTION', '').lower() == 'close':
                        break
            except GeneratorExit:
                listeners.remove(lambda new_value: send_update(new_value))
                raise

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

sse_manager = SSEManager()