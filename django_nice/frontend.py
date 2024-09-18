from nicegui import ui
import requests
from .config import Config

def bind_element_to_model(element, app_label, model_name, pk, field_name, element_id):
    """
    Bind a NiceGUI element to a Django model field via SSE for real-time updates.
    
    Args:
        element (ui.element): The NiceGUI element to bind.
        app_label (str): The Django app label.
        model_name (str): The Django model name.
        pk (int): The primary key of the model instance.
        field_name (str): The field name of the model to bind.
        element_id (str): The unique id of the HTML element.
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

    # Set the element's id and initial value
    element.props(f'id={element_id}')  # Correctly set the id using props()
    element.value = fetch_initial_data()
    
    # Bind the element to model updates via SSE
    element.on('update:modelValue', lambda e: update_data(e.args[0]))

    # Inject JavaScript for listening to SSE updates, finding the element by id
    sse_url = f'{host}{api_endpoint}/sse/{app_label}/{model_name}/{field_name}/'
    
    # Use ui.add_body_html to insert the <script> tag correctly
    ui.add_body_html(f"""
    <script>
        const eventSource = new EventSource('{sse_url}');
        eventSource.onmessage = function(event) {{
            document.getElementById('{element_id}').value = event.data;
        }};
    </script>
    """)
