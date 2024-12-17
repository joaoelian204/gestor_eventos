#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Set default superuser credentials using environment variables or fallback values
username=${DJANGO_SUPERUSER_USERNAME:-'admin_django'}
email=${DJANGO_SUPERUSER_EMAIL:-'admin@example.com'}
password=${DJANGO_SUPERUSER_PASSWORD:-'admin123'}

# Create superuser if it doesn't already exist
echo "Creating superuser if it doesn't already exist..."
echo "
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    if not User.objects.filter(username='$username').exists():
        User.objects.create_superuser('$username', '$email', '$password')
        print('Superuser created successfully.')
    else:
        print('Superuser already exists.')
except Exception as e:
    print(f'Error creating superuser: {e}')
" | python manage.py shell

