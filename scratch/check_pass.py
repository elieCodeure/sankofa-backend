import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sankhofa_backend.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

emails_to_test = ["client@gmail.com", "vendor@gmail.com", "shipper@gmail.com"]
for email in emails_to_test:
    try:
        user = User.objects.get(email=email)
        is_correct = user.check_password("password123")
        print(f"{email}: password123 is {'CORRECT' if is_correct else 'INCORRECT'}")
    except User.DoesNotExist:
        pass
