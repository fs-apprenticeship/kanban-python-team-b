## Setup
### Requirements
* Python 3.12+
* uv (see: [Installing uv](https://docs.astral.sh/uv/getting-started/installation/))

### Dependencies
Install packages: ``uv sync``
> Note: uv creates a venv for you under ``.venv/`` and will automatically keep it in sync with the package lock.

### Environment variables
Make a file in the project root called ``.env``
* ``SECRET_KEY`` (string) master key for cryptography

Generate a ``SECRET_KEY`` in Python:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Development
Run dev server: ``uv run python manage.py runserver``
