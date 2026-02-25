# Seed superuser
uv run manage.py createsuperuser --noinput || echo "Skipping superuser creation"

# Collect static files
uv run manage.py collectstatic --no-input --clear
