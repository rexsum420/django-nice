# django-nice

`django-nice` is a Python library designed to seamlessly integrate Django models with NiceGUI elements and Server-Sent Events (SSE) for real-time synchronization. This library allows you to bind NiceGUI frontend components (such as text areas, input fields, etc.) to Django model fields, ensuring that changes to either the backend or the frontend are synchronized in real-time.

## Why Use django-nice?

When working with Django and NiceGUI, binding frontend elements directly to Django models in a dynamic, real-time manner can be challenging. Out-of-the-box integrations often rely on manual updates, polling, or heavy reliance on traditional forms, which can be slow or cumbersome for modern web applications that require seamless real-time interactions.

`django-nice` solves these challenges by:

1. **Real-Time Sync with SSE**: The library leverages **Server-Sent Events (SSE)** to keep the frontend NiceGUI elements in sync with the backend Django models in real-time. Whenever the backend data changes, the frontend is updated immediately without needing to refresh or manually poll.

2. **Bidirectional Data Binding**: The library allows changes in the frontend to automatically update the corresponding Django model, and vice versa. This ensures consistency between the client and the server.

3. **REST API-Based Updates**: The library expose model fields as API endpoints. This makes the process of updating the Django backend from the frontend smooth, without needing to implement complex form handling.

### Advantages Over Regular Django-NiceGUI Integration:

- **Real-Time Updates**: Standard Django-NiceGUI integration doesn’t automatically sync data between the frontend and backend in real-time. `django-nice` provides automatic updates through SSE, allowing the frontend to reflect changes as soon as they happen in the backend.
- **Effortless Binding**: Instead of manually writing JavaScript, forms, or custom API calls to keep frontend elements in sync with Django models, `django-nice` handles this for you with minimal configuration.
- **Improved User Experience**: By offering real-time data updates, the library enhances the responsiveness of your NiceGUI app, creating a smoother and more interactive user experience.

## Tutorial

In your project's `urls.py` file, add the necessary API and SSE endpoints, this tutorial will use custom `.env` variables:

### 1.0 Installation and settings

After installing the package `django-nice`, just edit your `settings.py` file:

```python
INSTALLED_APPS += [
   'corsheaders'
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
]
CORS_ALLOW_ALL_ORIGINS = True
```

Yes don't forget to install also `corsheaders` package.

### 1.1 Define the model endpoints inside Django

```python
from django_nice.config import Config
from dotenv import load_dotenv
import os

load_dotenv()


config = Config.configure(
    host=os.getenv("DJANGO_DOMAIN") + ":" + os.getenv("DJANGO_PORT"),
    api_endpoint=os.getenv("NICEGUI_ENDPOINT"),
    require_auth=True, # By default this value is True
)
config.add_urls_to_project(urlpatterns, app_label="your-app", model_name="User")
```

### 1.2 Create a custom user model

As we need for login a new parameter that is saved as field inside the Django User model we need a custom User model to be able to do that.
Just follows a tutorial for this, like [this one](https://testdriven.io/blog/django-custom-user-model/) and add a new parameter like:

```
token = models.CharField(max_length=65, unique=True)
```

### 1.3 Add `.env` variables

```
DJANGO_SETTINGS_MODULE=your-app.settings
DJANGO_PORT="8000"
DJANGO_DOMAIN="http://localhost"

NICEGUI_STORAGE_SECRETKEY=your-secret
NICEGUI_ENDPOINT=api
NICEGUI_HOST="http://localhost"
NICEGUI_PORT="8080"
```

### 2. Create NiceGUI server

Consider that you can organize as you prefer this application but for this tutorial it will be just one NiceGUI file that include also the Login system.
Copy that content and create a file inside the root folder where is your `urls.py` file, call it as example `frontend.py`.

PS: check the code comments that explain some things.

```
#!usr/bin/env python
import binascii
import os
import django
import jwt

from django_nice.frontend import bind_element_to_model
from django_nice.config import Config
from django.contrib.auth import aauthenticate
from django.utils.decorators import sync_and_async_middleware
from django.conf import settings
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
from nicegui import ui
from nicegui import app

load_dotenv()
django.setup()

async def login_save(user):
    await ui.context.client.connected()
    payload = {"token": binascii.hexlify(os.urandom(30)).decode()}
    user.token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    await sync_to_async(user.save)()
    app.storage.tab.update({"user_id": user.id, "token": user.token}) # We are using https://nicegui.io/documentation/storage


async def logout_save():
    await ui.context.client.connected()
    user = await get_logged_user()
    user.token = ""
    await sync_to_async(user.save)()
    app.storage.tab.clear()


async def is_logged():
    await ui.context.client.connected()
    if os.getenv("DEBUG"):
        from your_app.models.users import User

        user = await wrap_async(User.objects.get, id=1) # In this way you can calls Django methods inside NiceGUI
        login_save(user)
        return True
    return app.storage.tab.get("token", False)


async def get_logged_user():
    from your_app.models.users import User

    user_id = app.storage.tab.get("user_id", False)
    return await wrap_async(User.objects.get, id=user_id) # In this way you can calls Django methods inside NiceGUI


async def wrap_async(method, **parameters):
    return await sync_to_async(method)(**parameters)


Config.configure(
    host=os.getenv("DJANGO_DOMAIN") + ":" + os.getenv("DJANGO_PORT"),
    api_endpoint="/" + os.getenv("NICEGUI_ENDPOINT"),
    require_auth=True,  # By default `require_auth` is set to True
)


@ui.page("/logout")
async def logout() -> None:
    await logout_save()
    ui.navigate.to("/login")


@ui.page("/login")
@sync_and_async_middleware
async def login() -> RedirectResponse | None:
    async def try_login() -> None:
        user = await aauthenticate(username=username.value, password=password.value) # This is already async
        if user is not None:
            await login_save(user)
            ui.navigate.to(app.storage.user.get("referrer_path", "/"))
        else:
            ui.notify("Wrong username or password", color="negative")

    if await is_logged():
        ui.navigate.to(app.storage.user.get("referrer_path", "/"))

    with ui.card().classes("absolute-center"):
        username = ui.input("Username").on("keydown.enter", try_login)
        password = ui.input("Password", password=True, password_toggle_button=True).on("keydown.enter", try_login)
        ui.button("Log in", on_click=try_login)
    return None

@ui.page("/")
async def index():
    if await is_logged():
        user = await get_logged_user()
        ui.label("Welcome " + user.username)
        inputbox = ui.input("").style("width: 25%")
        bind_element_to_model(
            inputbox,
            app_label="your-app",
            model_name="User",
            object_id=user.id,
            fields=["email"],
            element_id="email",
            token=user.token, # the token already saved to the user is used to match iff it is valid
        )
    else:
        ui.navigate.to("/login")

ui.run(
    host=os.getenv("NICEGUI_HOST").replace("http://", ""),
    port=int(os.getenv("NICEGUI_PORT")),
    storage_secret=os.getenv("NICEGUI_STORAGE_SECRETKEY"), # We use it to save some data on browser side for login stuff
)
```

This code includes a full login system in NiceGUI, if `DEBUG` is set automatically login as the first user in the DB and create a custom function `wrap_async` used to call Django method (that are sync, in a async way).

## Start servers for both apps

```bash
(venv)$ ./manage.py runserver 0.0.0.0:8000
Server started on port 8000
```
in a different terminal

```bash
(venv)$ python3 frontend/frontend.py
Server started on port 8080
```

## Notes

### 1. **Dynamic Binding with `dynamic_query`**

- The `bind_element_to_model` function supports **dynamic queries** (`dynamic_query` parameter), which allows model instances to be retrieved dynamically based on any criteria (e.g., a logged-in user's ID, the current high score, etc.).

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

### 2. **Binding Multiple Fields to a Single UI Element**

- The function allows **binding multiple fields** of a model instance to a single UI element. This is achieved by passing a list of fields through the `fields` parameter.

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
