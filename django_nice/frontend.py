from nicegui import ui
import requests
from .config import Config

def bind_element_to_model(element, app_label, model_name, object_id, field_name, element_id, property_name='value'):
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
        if value is None or value == '':
            pass
        else:
            url = f'{host}{api_endpoint}/{app_label}/{model_name}/{object_id}/{field_name}/'
            response = requests.post(url, json={field_name: value})

    # Set the element's initial value and bind the value between frontend and backend
    setattr(element, property_name, fetch_initial_data())

    # Determine the appropriate event listener based on the element type
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

    # Bind the element's value to backend model changes
    def on_frontend_change(e):
        new_value = ''.join(e.args)
        update_data(new_value)

    # Define the event listener for the frontend change
    element.on(listener_event, on_frontend_change)
    
    # Add a class to the element and an id for targeting via JavaScript
    element.props(f'class=model-element-class id={element_id}')

    # Define a callback that can be used in the injected JavaScript
    def set_value_in_element(new_value):
        element.set_value(new_value)

    # Inject JavaScript to listen to SSE updates and update the input element within the label
    sse_url = f'{host}{api_endpoint}/sse/{app_label}/{model_name}/{object_id}/{field_name}/'
    ui.add_body_html(f"""
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                let eventSource = new EventSource("{sse_url}");

                eventSource.onmessage = function(event) {{
                    const newValue = event.data;
                    console.log("Received new message from SSE:", newValue);

                    // Find the element of type {element_tag} with class 'model-element-class' and id '{element_id}'
                    const element = document.querySelector('.model-element-class {element_tag}[list="{element_id}-datalist"]');

                    if (element) {{
                        // Determine how to set the value based on element type
                        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA' || element.tagName === 'SELECT') {{
                            element.value = newValue;  // Update value for input-like elements
                        }} else if (element.tagName === 'BUTTON') {{
                            // You might want to update button text or trigger other effects
                            element.textContent = newValue;
                        }} else {{
                            element.textContent = newValue;  // Update content for other elements
                        }}
                        console.log("Updated element with ID:", '{element_id}', "to new value:", newValue);
                    }} else {{
                        console.error("Element with ID", '{element_id}', "not found in the class list.");
                    }}
                }};

                eventSource.onerror = function(error) {{
                    console.error("SSE connection error:", error);
                }};

                // Cleanup: Close the EventSource connection when the page is closed or navigated away from
                window.addEventListener('beforeunload', function() {{
                    if (eventSource) {{
                        eventSource.close();
                    }}
                }});
            }});
        </script>
    """)
