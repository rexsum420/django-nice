from setuptools import setup, find_packages

setup(
    name='django-nice',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'Django>=3.2',
        'djangorestframework',
        'django-sse',
        'nicegui',
    ],
    author='Jeffery Springs',
    description='Library to bind Django models with NiceGUI elements using DRF and SSE.',
    url='https://github.com/rexsum420/django-nice',
)
