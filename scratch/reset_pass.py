import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sankhofa_backend.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

users = User.objects.all()
for user in users:
    user.set_password("password123")
    user.save()

print("Tous les mots de passe ont ete reinitialises a 'password123'.")
