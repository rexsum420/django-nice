from nicegui import ui
import requests
from .config import Config

def bind_element_to_model(element, app_label, model_name, object_id, field_name, element_id, property_name='value'):
    host = Config.get_host()
    api_endpoint = Config.get_api_endpoint()

    def fetch_initial_data():
        url = f'{host}{api_endpoint}/{app_label}/{model_name}/{object_id}/{field_name}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get(field_name, '')
        return ''

    def update_data(value):
        if value is None or value == '':
            print("Error: Value is empty or None")
        else:
            url = f'{host}{api_endpoint}/{app_label}/{model_name}/{object_id}/{field_name}/'
            response = requests.post(url, json={field_name: value})
            print(f"Sent value: {value}, Response: {response.status_code}")

    setattr(element, property_name, fetch_initial_data())

    if isinstance(element, ui.input):
        listener_event = 'update:model-value'
    elif isinstance(element, ui.checkbox):
        listener_event = 'update:model-checked'
    elif isinstance(element, ui.slider):
        listener_event = 'update:model-value'
    elif isinstance(element, ui.button):
        listener_event = 'click'
    else:
        listener_event = f'update:model-{property_name}'

    def on_frontend_change(e):
        new_value = ''.join(e.args)
        update_data(new_value)

    element.on(listener_event, on_frontend_change)

    sse_url = f'{host}{api_endpoint}/sse/{app_label}/{model_name}/{object_id}/{field_name}/'
    ui.add_body_html(f"""
        <script>
            let eventSource = new EventSource("{sse_url}");

            eventSource.onmessage = function(event) {{
                const newValue = event.data;

                // Update the NiceGUI element dynamically via the framework
                const element = nicegui.elements['{element_id}'];
                if (element) {{
                    element['{property_name}'] = newValue;
                }}
            }};

            // Cleanup: Close the EventSource connection when the page is closed or navigated away from
            window.addEventListener('beforeunload', function() {{
                if (eventSource) {{
                    eventSource.close();
                }}
            }});
        </script>
    """)

    element.props(f'id={element_id}')
