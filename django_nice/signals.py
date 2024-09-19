from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from .sse import SSEManager

@receiver(post_save)
def model_update_signal(sender, instance, **kwargs):
    # Iterate over the model's fields and notify listeners if they have changed
    for field in instance._meta.fields:
        field_name = field.name
        new_value = getattr(instance, field_name, None)

        if new_value is not None:
            SSEManager.notify_listeners(sender.__name__, instance.pk, field_name, new_value)
