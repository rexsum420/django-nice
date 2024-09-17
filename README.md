# Installation: 

```bash
pip install django-nice
```

## Usage:

set these settings in your settings.py file:

```python
from django_nice.config import Config

# Configure the base URL (host) for the API
Config.configure(host='http://your-production-server.com', api_endpoint='/api')
```

add these to your projects urls.py file:

```python
from django_nice.config import Config

# Register API and SSE endpoints for a model (e.g., Data model in app 'myapp')
Config.add_urls_to_project(urlpatterns, app_label='myapp', model_name='Data')
```

then use inside your NiceGUI component like this:

```python
from nicegui import ui
from django_nice.frontend import bind_element_to_model

@ui.page('/')
def index():
    textarea = ui.textarea('This is data that is bound to the django model').classes('w-full')
    bind_element_to_model(textarea, app_label='myapp', model_name='Data', pk=1, field_name='data_to_display')

ui.run()
```