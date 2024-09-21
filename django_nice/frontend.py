from nicegui import ui
import requests
from .config import Config
from django.apps import apps
from django.db import models

def bind_element_to_model(element, app_label, model_name, object_id=None, fields=None, element_id=None, 
                          property_name='value', dynamic_query=None):
    if fields is None or not isinstance(fields, list):
        return  # Fail gracefully if no fields are provided
    
    host = Config.get_host()
    api_endpoint = Config.get_api_endpoint()
    model = apps.get_model(app_label, model_name)
    
    # Use dynamic queries (e.g., find by user ID or high score) if provided
    if dynamic_query:
        instance = model.objects.filter(**dynamic_query).first()
        if instance:
            object_id = instance.pk
        else:
            return  # No instance found for the dynamic query
    
    if not object_id:
        return  # Fail gracefully if object_id is still None
    
    # Fetch initial data for all fields
    def fetch_initial_data():
        data = {}
        for field_name in fields:
            url = f'{host}{api_endpoint}/{app_label}/{model_name}/{object_id}/{field_name}'
            response = requests.get(url)
            if response.status_code == 200:
                data[field_name] = response.json().get(field_name, '')
            else:
                data[field_name] = ''
        return data

    # Update data for a specific field
    def update_data(field_name, value):
        if value is None or value == '':
            pass
        else:
            url = f'{host}{api_endpoint}/{app_label}/{model_name}/{object_id}/{field_name}/'
            requests.post(url, json={field_name: value})

    # Initialize the element with combined data from all fields
    initial_data = fetch_initial_data()
    combined_data = ', '.join([f'{field}: {initial_data[field]}' for field in fields])
    setattr(element, property_name, combined_data)

    # Listener events based on the element type
    if isinstance(element, ui.input):
        listener_event = 'update:model-value'
        element_tag = 'input'
    elif isinstance(element, ui.checkbox):
        listener_event = 'update:model-checked'
        element_tag = 'input[type="checkbox"]'
    elif isinstance(element, ui.slider):
        listener_event = 'update:model-value'
        element_tag = 'input[type="range"]'
    elif isinstance(element, ui.textarea):
        listener_event = 'update:model-value'
        element_tag = 'textarea'
    elif isinstance(element, ui.button):
        listener_event = 'click'
        element_tag = 'button'
    else:
        listener_event = f'update:model-{property_name}'
        element_tag = '*'

    # Handle frontend changes by updating the respective field in the model
    def on_frontend_change(e):
        new_value = ''.join(e.args).split(', ')
        field_values = {field: value for field, value in zip(fields, new_value)}
        for field_name, value in field_values.items():
            update_data(field_name, value)

    element.on(listener_event, on_frontend_change)
    
    element.props(f'class=model-element-class id={element_id}')

    # Set up Server-Sent Events (SSE) to update the element when any field changes
    def set_value_in_element(new_data):
        combined_data = ', '.join([f'{field}: {new_data[field]}' for field in fields])
        element.set_value(combined_data)

    for field_name in fields:
        sse_url = f'{host}{api_endpoint}/sse/{app_label}/{model_name}/{object_id}/{field_name}/'
        ui.add_body_html(f"""
            <script>
                document.addEventListener("DOMContentLoaded", function() {{
                    let eventSource = new EventSource("{sse_url}");

                    eventSource.onmessage = function(event) {{
                        const newValue = event.data;
                        const element = document.querySelector('.model-element-class {element_tag}[list="{element_id}-datalist"]');

                        if (element) {{
                            let current_value = element.value || element.textContent;
                            let new_field_data = '{field_name}: ' + newValue;

                            if (current_value.includes('{field_name}:')) {{
                                // Replace only the specific field value
                                const updated_value = current_value.replace(new RegExp('{field_name}:.*?(,|$)'), new_field_data + '$1');
                                element.value = updated_value;
                            }} else {{
                                // Append if field data doesn't exist
                                element.value += ', ' + new_field_data;
                            }}
                        }} else {{
                            console.error("Element with ID", '{element_id}', "not found in the class list.");
                        }}
                    }};

                    eventSource.onerror = function(error) {{
                        console.error("SSE connection error:", error);
                    }};

                    window.addEventListener('beforeunload', function() {{
                        if (eventSource) {{
                            eventSource.close();
                        }}
                    }});
                }});
            </script>
        """)

