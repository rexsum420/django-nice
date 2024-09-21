# django-nice

`django-nice` is a Python library designed to seamlessly integrate Django models with NiceGUI elements using Django REST Framework (DRF) and Server-Sent Events (SSE) for real-time synchronization. This library allows you to bind NiceGUI frontend components (such as text areas, input fields, etc.) to Django model fields, ensuring that changes to either the backend or the frontend are synchronized in real-time.

## Why Use django-nice?

When working with Django and NiceGUI, binding frontend elements directly to Django models in a dynamic, real-time manner can be challenging. Out-of-the-box integrations often rely on manual updates, polling, or heavy reliance on traditional forms, which can be slow or cumbersome for modern web applications that require seamless real-time interactions.

`django-nice` solves these challenges by:

1. **Real-Time Sync with SSE**: The library leverages **Server-Sent Events (SSE)** to keep the frontend NiceGUI elements in sync with the backend Django models in real-time. Whenever the backend data changes, the frontend is updated immediately without needing to refresh or manually poll.

2. **Bidirectional Data Binding**: The library allows changes in the frontend to automatically update the corresponding Django model, and vice versa. This ensures consistency between the client and the server.

3. **REST API-Based Updates**: It uses Django REST Framework (DRF) to expose model fields as API endpoints. This makes the process of updating the Django backend from the frontend smooth, without needing to implement complex form handling.

### Advantages Over Regular Django-NiceGUI Integration:

- **Real-Time Updates**: Standard Django-NiceGUI integration doesn’t automatically sync data between the frontend and backend in real-time. `django-nice` provides automatic updates through SSE, allowing the frontend to reflect changes as soon as they happen in the backend.
- **Effortless Binding**: Instead of manually writing JavaScript, forms, or custom API calls to keep frontend elements in sync with Django models, `django-nice` handles this for you with minimal configuration.
- **Improved User Experience**: By offering real-time data updates, the library enhances the responsiveness of your NiceGUI app, creating a smoother and more interactive user experience.

## Usage:

In your project's `urls.py` file, add the necessary API and SSE endpoints:

```python
from django_nice.config import Config

# Register API and SSE endpoints for a model (e.g., Data model in app 'myapp')
Config.add_urls_to_project(
    urlpatterns, 
    app_label='myapp', 
    model_name='DataModel', 
    field_name='data_to_display', 
    object_id=1
)
```

### Bind Frontend Elements to Django Models:

Inside your NiceGUI components, bind frontend elements (like text areas) to Django model fields for real-time updates:

```python
from nicegui import ui
from django_nice.frontend import bind_element_to_model
from django_nice.config import Config

Config.configure(host='http://127.0.0.1:8000', api_endpoint='/api')

@ui.page('/')
def index():
    inputbox = ui.input('').style('width: 25%')
    bind_element_to_model(
        inputbox,
        app_label='myapp',
        model_name='DataModel',
        object_id=1,
        field_name='data_to_display',
        element_id='bound_input'
    )

ui.run(host='127.0.0.1', port=8080)
```

This example shows how to bind a NiceGUI `input` element to a Django model field, ensuring real-time synchronization between the frontend and backend. When the Django model changes, the `input` is updated automatically, and any changes made in the `input` are sent to the backend immediately.

Defining a property of the element is also possible but optional. here's how you would set the content property of a markdown element:

```python
    markdown = ui.markdown().styles('background-color:black;color:white')
    bind_element_to_model(
        markdown,
        app_label='myapp',
        model_name='DataModel',
        pk=1,
        field_name='data_to_display'
        element_id='bound_markdown',
        property_name='content'
    )
```

### Full walkthrough to setup
To get started, follow these steps:

```bash
$ virtualenv env
created virtual environment CPython3.11.9.final.0-64 in 11358ms
  creator CPython3Posix(dest=/home/rexsum/rust/django/demo/env, clear=False, no_vcs_ignore=False, global=False)
  seeder FromAppData(download=False, pip=bundle, setuptools=bundle, wheel=bundle, via=copy, app_data_dir=/home/rexsum/.local/share/virtualenv)
    added seed packages: pip==24.2, setuptools==70.3.0, wheel==0.44.0
  activators BashActivator,CShellActivator,FishActivator,NushellActivator,PowerShellActivator,PythonActivator
                                                                                                               $ source env/bin/activate 
                                                                                                               (venv)$ pip install django django-nice nicegui 
Collecting django...

(venv)$ django-admin startproject demo . 

(venv)$ ./manage.py startapp people
```

## Define a model:

```python
from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    score = models.PositiveIntegerField()
    
    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.score}'
```
```bash
(venv)$ ./manage.py makemigrations

(venv)$ ./manage.py migrate

(venv)$ mkdir frontend && cd frontend 

(venv)$ touch __init__.py && touch main.py
```

## inside main.py:

```python
from nicegui import ui
from django_nice.frontend import bind_element_to_model
from people.models import Person
from django_nice.config import Config

Config.configure(host='http://127.0.0.1:8000', api_endpoint='/api')

@ui.page('/')
def index():
    inputbox = ui.input('').style('width: 25%')
    bind_element_to_model(
        inputbox,
        app_label='people',
        model_name='Person',
        object_id=1,
        field_name='first_name',
        element_id='firstName'
    )

ui.run(host='127.0.0.1', port=8080)
```

## inside of demo.urls:

```python
from django.contrib import admin
from django.urls import path,include
from django_nice.config import Config

urlpatterns = [
    path('admin/', admin.site.urls),
    path('people/', include('people.urls')),
]

Config.add_urls_to_project(
    urlpatterns,
    app_label='people',
    model_name='Person',
    field_name='first_name',
    object_id=1
)
```

## Create a view and url_pattern to redirect HTTPResponses to the NiceGUI app  

`people.urls`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.frontend_view, name='frontend'),
]
```

`people.view`:

```python
from django.http import HttpResponseRedirect

def frontend_view(request):
    return HttpResponseRedirect('http://127.0.0.1:8080/')
```

## Make changes in settings.py

```python
INSTALLED_APPS = [
   'people'
   'corsheaders'
]
MIDDLEWEAR = [
'corsheaders.middleware.CorsMiddleware', 
]
CORS_ALLOW_ALL_ORIGINS = True
```

## Start servers for both apps

```bash
(venv)$ ./manage.py runserver 0.0.0.0:8000
Server started on port 8000
```
in a different terminal

```bash
(venv)$ python3 frontend/main.py
Server started on port 8080
```
## Installation:

To install the library, simply run:

`pip install django-nice`


### Updates to version 0.5.0

### Description of Updates and Extensions Made to the `django_nice` Library

The recent updates and extensions to the `django_nice` library have significantly increased its flexibility, allowing for more dynamic data binding and supporting complex use cases such as binding multiple fields to a single UI element, handling user-specific data dynamically, and enabling real-time updates with Server-Sent Events (SSE). Below is a detailed breakdown of the changes:

---

### 1. **Dynamic Binding with `dynamic_query`**

**Previous Version:**
- The library required a static `object_id` to bind a UI element to a single field of a specific model instance.

**Update:**
- The `bind_element_to_model` function now supports **dynamic queries** (`dynamic_query` parameter), which allows model instances to be retrieved dynamically based on any criteria (e.g., a logged-in user's ID, the current high score, etc.).
  
  **New Features:**
  - You can now bind UI elements to objects retrieved dynamically, without needing to know the `object_id` in advance.
  - This is useful for scenarios like binding a UI element to the current user's data or retrieving a model instance based on specific business logic (e.g., highest score).

**Example:**
```python
bind_element_to_model(
    element,
    app_label='people',
    model_name='Person',
    dynamic_query={'id': request.user.id},  # Bind to the logged-in user's instance
    field_name='first_name',
    element_id='userFirstName'
)
```

---

### 2. **Binding Multiple Fields to a Single UI Element**

**Previous Version:**
- The `bind_element_to_model` function only supported binding one field of a model instance to a UI element.

**Update:**
- The function was enhanced to allow **binding multiple fields** of a model instance to a single UI element. This is achieved by passing a list of fields through the `fields` parameter.

  **New Features:**
  - Multiple fields (e.g., `first_name`, `last_name`, `age`) can now be combined and displayed within a single element.
  - The values are fetched from the model instance, combined into a string (e.g., `first_name: John, last_name: Doe`), and displayed in the UI element.
  - Real-time updates (via SSE) are handled individually for each field, ensuring that when any of the bound fields change, the element updates without interfering with other fields.

**Example:**
```python
bind_element_to_model(
    element,
    app_label='people',
    model_name='Person',
    fields=['first_name', 'last_name', 'age'],  # Bind multiple fields
    element_id='personInfo'
)
```

**Benefits:**
- This feature is ideal for displaying a summary of multiple fields in one UI element, such as showing a user's full profile (name, email, age) in a single input or text area.

---

### 3. **Improved SSE (Server-Sent Events) Integration**

**Previous Version:**
- SSE was set up to broadcast changes for a single field in real-time.

**Update:**
- SSE was extended to support **multiple fields** being bound to a single UI element. Now, when any of the bound fields changes, the specific field's value is updated within the element.
  
  **New Features:**
  - Each field has its own SSE stream, and when data changes on the server (e.g., via a Django model update), the new field value is pushed to the client.
  - The UI element reflects the updated values in real-time, without needing to reload the page or manually refresh the data.

**Example:**
- If the `first_name` field changes in the database, the SSE system will update only the `first_name` portion of the element's value.

---

### 4. **Improved Update Handling in the Frontend**

**Previous Version:**
- Changes to the frontend were handled for a single field per element.

**Update:**
- The update logic was improved to handle multiple fields. Now, when a user modifies a value in the UI element that is bound to multiple fields, the changes are correctly split and sent back to the server, updating each field individually.

  **New Features:**
  - The `on_frontend_change` function now intelligently parses and updates multiple fields from the element’s content. It can detect and differentiate between changes in multiple field values (e.g., `first_name`, `last_name`), ensuring that the correct field is updated on the server.

**Example:**
```python
# When the frontend changes, the element can handle multiple fields being updated
def on_frontend_change(e):
    new_value = ''.join(e.args).split(', ')  # Split combined field data
    field_values = {field: value for field, value in zip(fields, new_value)}  # Map fields to new values
    for field_name, value in field_values.items():
        update_data(field_name, value)
```

---

### 5. **Support for Custom Element Types**

**Previous Version:**
- The system supported only a predefined set of UI elements (e.g., `ui.input`, `ui.checkbox`, `ui.slider`).

**Update:**
- Flexibility was added to support additional or custom element types. The logic now checks the type of element and sets up the correct event listeners and attributes for the given element type.

  **New Features:**
  - Support for custom event types or complex elements is easier to integrate by modifying how listeners and handlers are registered for each type of element.

---

### Summary of Key Improvements:
- **Dynamic Instance Selection**: Bind elements to dynamically retrieved instances, allowing flexible queries (e.g., by user ID or high score).
- **Multiple Field Binding**: Bind several fields from a model instance to a single UI element, combining their data and supporting real-time updates for each field.
- **Enhanced SSE Handling**: Improved real-time updates for multiple fields, ensuring that any change in a field is reflected in the bound UI element.
- **Custom Event Handling**: Support for different types of UI elements and their event listeners, making it more flexible for complex frontends.
  
---

These updates significantly extend the library's flexibility, allowing for more complex, dynamic front-end interactions driven by Django model data, while keeping it simple and intuitive to use.
