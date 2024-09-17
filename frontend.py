from nicegui import ui
import requests
from .config import Config

def bind_element_to_model(element, app_label, model_name, pk, field_name):
    """
    Bind a NiceGUI element to a Django model field via SSE for real-time updates.
    """
    # Fetch the host and API endpoint from the configuration
    host = Config.get_host()
    api_endpoint = Config.get_api_endpoint()

    # Fetch the initial data from Django
    def fetch_initial_data():
        url = f'{host}{api_endpoint}/{app_label}/{model_name}/{pk}/'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get(field_name, '')
        return ''

    # Update the model when the value changes in the frontend
    def update_data(value):
        url = f'{host}{api_endpoint}/{app_label}/{model_name}/{pk}/{field_name}/'
        response = requests.post(url, json={field_name: value})
        if response.status_code == 200:
            print('Data updated successfully!')

    # Bind the element to model updates via SSE
    element.value = fetch_initial_data()
    element.on('update:modelValue', lambda e: update_data(e.args[0]))

    # Inject JavaScript for listening to SSE
    sse_url = f'{host}{api_endpoint}/sse/{app_label}/{model_name}/{field_name}/'
    ui.html(f"""
    <script>
        const eventSource = new EventSource('{sse_url}');
        eventSource.onmessage = function(event) {{
            document.querySelector('textarea').value = event.data;
        }};
    </script>
    """)
