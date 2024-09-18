from django.http import JsonResponse
from django.views import View
from django.apps import apps

class ModelAPI(View):
    def get(self, request, app_label, model_name, object_id, field_name):
        # Fetch the model dynamically
        model = apps.get_model(app_label, model_name)
        try:
            # Retrieve the instance based on the object_id
            instance = model.objects.get(pk=object_id)
            
            # Dynamically get the value of the specified field
            field_value = getattr(instance, field_name)
            
            data = {
                field_name: field_value  # Respond with the dynamic field name and its value
            }
            return JsonResponse(data)
        except model.DoesNotExist:
            return JsonResponse({"error": "Object not found"}, status=404)

    def post(self, request, app_label, model_name, object_id):
        """
        Update the value of a specific model field.
        """
        model = apps.get_model(app_label, model_name)
        instance = model.objects.get(pk=object_id)
        field_name = request.GET.get('field', None)
        field_value = request.POST.get(field_name)

        if field_name and hasattr(instance, field_name):
            setattr(instance, field_name, field_value)
            instance.save()
            return JsonResponse({field_name: getattr(instance, field_name)})
        return JsonResponse({'error': 'Field not found or invalid data'}, status=400)
