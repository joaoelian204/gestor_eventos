#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser if it doesn't already exist
echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
username = 'admin_django'; \
email = 'admin@example.com'; \
password = 'admin123'; \
if not User.objects.filter(username=username).exists(): \
    User.objects.create_superuser(username, email, password); \
    print('Superuser created successfully.'); \
else: \
    print('Superuser already exists.');" | python manage.py shell

