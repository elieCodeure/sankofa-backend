import os
import sys
import django

# Add the project directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Setup django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sankhofa_backend.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
users = User.objects.all()

print("--- USERS ---")
if not users:
    print("Aucun utilisateur dans la base.")
else:
    for u in users:
        role = getattr(u, 'role', 'N/A')
        print(f"ID: {u.id} | Email: {u.email} | Role: {role} | Nom: {u.first_name} {u.last_name}")
print("-------------")
