# django-nice

`django-nice` is a Python library designed to seamlessly integrate Django models with NiceGUI elements using Django REST Framework (DRF) and Server-Sent Events (SSE) for real-time synchronization. This library allows you to bind NiceGUI frontend components (such as text areas, input fields, etc.) to Django model fields, ensuring that changes to either the backend or the frontend are synchronized in real-time.

## Why Use django-nice?

When working with Django and NiceGUI, binding frontend elements directly to Django models in a dynamic, real-time manner can be challenging. Out-of-the-box integrations often rely on manual updates, polling, or heavy reliance on traditional forms, which can be slow or cumbersome for modern web applications that require seamless real-time interactions.

`django-nice` solves these challenges by:

1. Real-Time Sync with SSE: The library leverages Server-Sent Events (SSE) to keep the frontend NiceGUI elements in sync with the backend Django models in real-time. Whenever the backend data changes, the frontend is updated immediately without needing to refresh or manually poll.

2. Bidirectional Data Binding: The library allows changes in the frontend to automatically update the corresponding Django model, and vice versa. This ensures consistency between the client and the server.

3. REST API-Based Updates: It uses Django REST Framework (DRF) to expose model fields as API endpoints. This makes the process of updating the Django backend from the frontend smooth, without needing to implement complex form handling.

### Advantages Over Regular Django-NiceGUI Integration:

- Real-Time Updates: Standard Django-NiceGUI integration doesn’t automatically sync data between the frontend and backend in real-time. `django-nice` provides automatic updates through SSE, allowing the frontend to reflect changes as soon as they happen in the backend.
- Effortless Binding: Instead of manually writing JavaScript, forms, or custom API calls to keep frontend elements in sync with Django models, `django-nice` handles this for you with minimal configuration.
- Improved User Experience: By offering real-time data updates, the library enhances the responsiveness of your NiceGUI app, creating a smoother and more interactive user experience.

## Usage:

To get started, follow these steps:

### 1. Configure the Base URL in settings.py:

Add the following to your `settings.py` file to configure the API endpoint:

from django_nice.config import Config

# Configure the base URL (host) for the API
Config.configure(host='http://your-production-server.com', api_endpoint='/api')

### 2. Register API and SSE Endpoints in urls.py:

In your project's `urls.py` file, add the necessary API and SSE endpoints:

from django_nice.config import Config

# Register API and SSE endpoints for a model (e.g., Data model in app 'myapp')
Config.add_urls_to_project(urlpatterns, app_label='myapp', model_name='Data')

### 3. Bind Frontend Elements to Django Models:

Inside your NiceGUI components, bind frontend elements (like text areas) to Django model fields for real-time updates:

from nicegui import ui
from django_nice.frontend import bind_element_to_model

@ui.page('/')
def index():
    textarea = ui.textarea('This is data that is bound to the django model').classes('w-full')
    bind_element_to_model(textarea, app_label='myapp', model_name='Data', pk=1, field_name='data_to_display')

ui.run()

This example shows how to bind a NiceGUI `textarea` element to a Django model field, ensuring real-time synchronization between the frontend and backend. When the Django model changes, the `textarea` is updated automatically, and any changes made in the `textarea` are sent to the backend immediately.

## Installation:

To install the library, simply run:

pip install django-nice
