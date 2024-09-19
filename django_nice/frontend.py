from nicegui import ui
import requests
from .config import Config 

def bind_element_to_model(element, app_label, model_name, object_id, field_name, element_id):
    host = Config.get_host()
    api_endpoint = Config.get_api_endpoint()

    # Fetch initial data from the model
    def fetch_initial_data():
        url = f'{host}{api_endpoint}/{app_label}/{model_name}/{object_id}/'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get(field_name, '')
        return ''

    # Update the model when the value changes in the frontend
    def update_data(value):
        url = f'{host}{api_endpoint}/{app_label}/{model_name}/{object_id}/{field_name}/'
        requests.post(url, json={field_name: value})

    # Set the element's initial value
    element.props(f'id={element_id}')
    element.value = fetch_initial_data()

    # Bind the element to model updates via SSE
    element.on('update:modelValue', lambda e: update_data(e.args[0]))

    # Inject JavaScript to listen to SSE updates
    sse_url = f'{host}{api_endpoint}/sse/{app_label}/{model_name}/{field_name}/'
    ui.add_body_html(f"""
    <script>
        const eventSource = new EventSource('{sse_url}');
        eventSource.onmessage = function(event) {{
            document.getElementById('{element_id}').value = event.data;
        }};
    </script>
    """)