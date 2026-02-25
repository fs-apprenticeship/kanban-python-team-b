## Setup
### Requirements
* Python 3.12+ via ``uv`` (see: [Installing uv](https://docs.astral.sh/uv/getting-started/installation/))
* Docker and Docker Compose

### Dependencies
Install packages: ``uv sync``
> Note: uv creates a venv for you under ``.venv/`` and will automatically keep it in sync with the package lock.

### Environment variables
Make a file in the project root called ``.env`` (see: ``.env.example``)
* ``SECRET_KEY`` (str) master key for cryptography
* ``DEBUG`` (bool) debug mode, must be set to ``False`` in production
* ``POSTGRES_DB``, ``POSTGRES_USER``, and ``POSTGRES_PASSWORD`` for database connection
* ``DJANGO_SUPERUSER_EMAIL`` and ``DJANGO_SUPERUSER_PASSWORD`` for quick [superuser creation](https://docs.djangoproject.com/en/6.0/ref/django-admin/#django-admin-createsuperuser)

#### Generate a ``SECRET_KEY`` in Python
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```
> Note: For development you can just use ``some-string``, but in production it's recommended to generate an actual key.

## Development
Start db container: ``docker compose up -d``

Apply migrations to db: ``uv run manage.py migrate``

Run dev server: ``uv run manage.py runserver``
