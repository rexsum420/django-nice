from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from .sse import SSEManager

@receiver(post_save)
def model_update_signal(sender, instance, **kwargs):
    for field in instance._meta.fields:
        field_name = field.name
        new_value = getattr(instance, field_name, None)

        if new_value is not None:
            SSEManager.notify_listeners(sender.__name__, instance.pk, field_name, new_value)

from django.db.models.signals import post_save

def setup_signals(app_label, model_name, signal_handler):
    model = apps.get_model(app_label, model_name)
    post_save.connect(signal_handler, sender=model)