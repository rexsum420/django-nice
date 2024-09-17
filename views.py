from rest_framework.response import Response
from rest_framework.views import APIView
from django.apps import apps
from django.http import Http404

class ModelUpdateAPIView(APIView):
    """
    A generic view to update any model via POST request.
    Users will specify the app name, model name, and field they want to update.
    """
    def post(self, request, app_label, model_name, pk, field_name):
        try:
            # Get the model class dynamically based on app_label and model_name
            model = apps.get_model(app_label, model_name)
        except LookupError:
            raise Http404("Model not found.")

        try:
            instance = model.objects.get(pk=pk)
        except model.DoesNotExist:
            raise Http404("Instance not found.")

        # Get the new value from the request data
        new_value = request.data.get(field_name)
        if new_value is not None:
            setattr(instance, field_name, new_value)
            instance.save()
            return Response({field_name: new_value})
        else:
            return Response({"error": f"Field '{field_name}' not found in request."}, status=400)
