from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from .sse import SSEManager

# Signal handler to track model field updates
@receiver(post_save)
def model_update_signal(sender, instance, field_name, **kwargs):
    new_value = getattr(instance, field_name, None)

    # Here you would notify the frontend via SSE or WebSockets
    if new_value is not None:
        SSEManager.notify_listeners(sender.__name__, instance.pk, field_name, new_value)
