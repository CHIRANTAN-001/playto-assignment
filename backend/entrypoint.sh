#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Seeding data..."
python manage.py seed

echo "Starting server..."
exec "$@"
