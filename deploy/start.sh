#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn store.wsgi:application --bind 0.0.0.0:8000 --access-logfile -
