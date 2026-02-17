## Setup
### Requirements
* Python 3.12+

### Dependencies
Install: ``python -m pip install -r requirements.txt``

### Environment variables
Make a file in the project root called ``.env``
* ``SECRET_KEY`` (string) master key for cryptography

Generate a ``SECRET_KEY`` in Python:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Development
Run dev server: ``python manage.py runserver``
