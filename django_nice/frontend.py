from nicegui import ui
import requests
from .config import Config 

def bind_element_to_model(element, app_label, model_name, object_id, field_name, element_id):
    host = Config.get_host()
    api_endpoint = Config.get_api_endpoint()

    # Fetch initial data from the model
    def fetch_initial_data():
        url = f'{host}{api_endpoint}/{app_label}/{model_name}/{object_id}/{field_name}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get(field_name, '')
        return ''

    # Update the model when the value changes in the frontend
    def update_data(value):
        url = f'{host}{api_endpoint}/{app_label}/{model_name}/{object_id}/{field_name}/'
        requests.post(url, json={field_name: value})

    # Set the element's initial value and bind the value between frontend and backend
    element.value = fetch_initial_data()

    # Bind the element's value to backend model changes
    def on_frontend_change(e):
        new_value = e.value  # Extract the new value
        update_data(new_value)  # Send updated value to the backend

    # Use NiceGUI's built-in binding mechanism for two-way data binding
    element.on('value_change', on_frontend_change)

    # Inject JavaScript to listen to SSE updates and update the element
    sse_url = f'{host}{api_endpoint}/sse/{app_label}/{model_name}/{object_id}/{field_name}/'
    ui.add_body_html(f"""
    <script>
        const eventSource = new EventSource('{sse_url}');
        eventSource.onmessage = function(event) {{
            const element = document.getElementById('{element_id}');
            const newValue = event.data;

            // Dispatch a proper input event to trigger frontend updates via NiceGUI
            const inputEvent = new Event('input', {{ bubbles: true }});
            element.value = newValue;
            element.dispatchEvent(inputEvent);  // Ensure NiceGUI handles the change
        }};
    </script>
    """)

    # Add ID to the element for proper access from the injected JavaScript
    element.props(f'id={element_id}')
