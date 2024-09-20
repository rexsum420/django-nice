from nicegui import ui
import requests
from .config import Config
from django.apps import apps
from django.db import models

def bind_element_to_model(element, app_label, model_name, object_id, field_name, element_id, property_name='value'):
    host = Config.get_host()
    api_endpoint = Config.get_api_endpoint()
    model = apps.get_model(app_label, model_name)
    field = model._meta.get_field(field_name)
    
    # Getting ready to add input validation
    
    # input_validation_js = ""
    
    # if isinstance(field, models.IntegerField):
    #     input_validation_js = f"""
    #     const element = document.querySelector('.model-element-class {element_tag}[list="{element_id}-datalist"]')
    #     element.addEventListener("input", function(event) {{
    #         let value = event.target.value;
    #         event.target.value = value.replace(/[^-0-9]/g, '');  // Allow integers, including negative
    #     }});
    #     """
    # elif isinstance(field, (models.DecimalField, models.FloatField)):
    #     input_validation_js = f"""
    #     const element = document.querySelector('.model-element-class {element_tag}[list="{element_id}-datalist"]')
    #     element.addEventListener("input", function(event) {{
    #         let value = event.target.value;
    #         event.target.value = value.replace(/[^-0-9.]/g, '');  // Allow decimal numbers
    #     }});
    #     """
    # elif isinstance(field, models.BooleanField):
    #     input_validation_js = ""
    # elif isinstance(field, models.EmailField):
    #     input_validation_js = f"""
    #     const element = document.querySelector('.model-element-class {element_tag}[list="{element_id}-datalist"]')
    #     element.addEventListener("input", function(event) {{
    #         let value = event.target.value;
    #         if (!value.match(/^[\\w.-]+@[\\w.-]+\\.[A-Za-z]+$/)) {{
    #             event.target.setCustomValidity("Invalid email format");
    #         }} else {{
    #             event.target.setCustomValidity("");
    #         }}
    #     }});
    #     """
    # elif isinstance(field, models.TextField):
    #     max_length = field.max_length if field.max_length else 10000
    #     input_validation_js = f"""
    #     document.querySelector("#{element_id}").maxLength = {max_length};
    #     """
    # elif isinstance(field, (models.PositiveIntegerField, models.PositiveBigIntegerField)):
    #     input_validation_js = f"""
    #     const element = document.querySelector('.model-element-class {element_tag}[list="{element_id}-datalist"]')
    #     element.addEventListener("input", function(event) {{
    #         let value = event.target.value;
    #         if (value && (isNaN(value) || value < 0)) {{
    #             event.target.value = value.replace(/[^0-9]/g, '');  // Only allow positive integers
    #         }}
    #     }});
    #     """
    # elif isinstance(field, models.CharField):
    #     max_length = field.max_length
    #     input_validation_js = f"""
    #     const element = document.querySelector('.model-element-class {element_tag}[list="{element_id}-datalist"]')
    #     element.maxLength = {max_length};
    #     """
    # elif isinstance(field, models.BinaryField):
    #     input_validation_js = ""

    def fetch_initial_data():
        url = f'{host}{api_endpoint}/{app_label}/{model_name}/{object_id}/{field_name}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get(field_name, '')
        return ''

    def update_data(value):
        if value is None or value == '':
            pass
        else:
            url = f'{host}{api_endpoint}/{app_label}/{model_name}/{object_id}/{field_name}/'
            response = requests.post(url, json={field_name: value})

    setattr(element, property_name, fetch_initial_data())

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

    def on_frontend_change(e):
        new_value = ''.join(e.args)
        update_data(new_value)

    element.on(listener_event, on_frontend_change)
    
    element.props(f'class=model-element-class id={element_id}')

    def set_value_in_element(new_value):
        element.set_value(new_value)

    sse_url = f'{host}{api_endpoint}/sse/{app_label}/{model_name}/{object_id}/{field_name}/'
    ui.add_body_html(f"""
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                let eventSource = new EventSource("{sse_url}");

                eventSource.onmessage = function(event) {{
                    const newValue = event.data;
                    const element = document.querySelector('.model-element-class {element_tag}[list="{element_id}-datalist"]');

                    if (element) {{
                        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA' || element.tagName === 'SELECT') {{
                            element.value = newValue;
                        }} else if (element.tagName === 'BUTTON') {{
                            element.textContent = newValue;
                        }} else {{
                            element.textContent = newValue;
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
