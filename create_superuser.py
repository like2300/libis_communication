# create_superuser.py

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "libis_communication.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = "admin"
password = "root"
email = "admin@example.com"

if not User.objects.filter(username=username).exists():
    print(f"Création de l'utilisateur {username}...")
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    print(f"L'utilisateur {username} existe déjà.")
