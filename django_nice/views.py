from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
from django.apps import apps

@method_decorator(csrf_exempt, name='dispatch')
class ModelAPI(View):
    def get(self, request, app_label, model_name, object_id, field_name):
        model = apps.get_model(app_label, model_name)
        try:
            instance = model.objects.get(pk=object_id)
            field_value = getattr(instance, field_name)
            data = {
                field_name: field_value
            }
            return JsonResponse(data)
        except model.DoesNotExist:
            return JsonResponse({"error": "Object not found"}, status=404)

    def post(self, request, app_label, model_name, object_id, field_name):
        model = apps.get_model(app_label, model_name)
        instance = model.objects.get(pk=object_id)
        field_value = request.POST.get(field_name)

        if field_name and hasattr(instance, field_name):
            setattr(instance, field_name, field_value)
            instance.save()
            return JsonResponse({field_name: getattr(instance, field_name)})
        return JsonResponse({'error': 'Field not found or invalid data'}, status=400)
