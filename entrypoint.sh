#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating default superuser..."
python manage.py shell <<EOF
from apps.accounts.models import User
if not User.objects.filter(email='admin@admin.com').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@admin.com',
        password='admin123',
        role='admin'
    )
    print('✓ Superuser created: admin@admin.com / admin123')
else:
    print('✓ Superuser already exists')
EOF

echo "Starting gunicorn on 0.0.0.0:8000..."
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 --access-logfile - --error-logfile - config.wsgi:application
