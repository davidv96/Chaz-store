#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py shell --no-imports -c '
import os

from django.contrib.auth import get_user_model

user_model = get_user_model()
email = os.environ["DJANGO_SUPERUSER_EMAIL"]
if not user_model.objects.filter(email=email).exists():
    user_model.objects.create_superuser(email, os.environ["DJANGO_SUPERUSER_PASSWORD"])
'
exec python manage.py runserver 0.0.0.0:8000
