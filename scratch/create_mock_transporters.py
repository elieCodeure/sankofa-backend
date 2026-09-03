import os
import sys
import django

# Setup django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sankhofa_backend.settings')
django.setup()

from accounts.models import CustomUser, UserProfile
from django.db import transaction

def create_or_update_transporter(email, first_name, last_name, business_name, vehicle_type, coverage_area, phone_number):
    with transaction.atomic():
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'role': 'TRANSPORTER',
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True
            }
        )
        if created:
            user.set_password('sankhofa123')
            user.save()
            print(f"Created user {email}")
        else:
            user.role = 'TRANSPORTER'
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            print(f"Updated user {email}")

        profile, p_created = UserProfile.objects.get_or_create(user=user)
        profile.is_verified = True
        profile.business_name = business_name
        profile.vehicle_type = vehicle_type
        profile.coverage_area = coverage_area
        profile.phone_number = phone_number
        profile.save()
        print(f"Set profile for {email} (verified={profile.is_verified}, vehicle={profile.vehicle_type}, coverage={profile.coverage_area})")

if __name__ == '__main__':
    print("Seeding mock transporters...")
    
    # 1. Update existing shipper
    create_or_update_transporter(
        email='shipper@gmail.com',
        first_name='Shipper',
        last_name='Express',
        business_name='Shipper Express',
        vehicle_type='VAN',
        coverage_area='Ouagadougou, Lomé, Cotonou',
        phone_number='+226 70 00 00 01'
    )
    
    # 2. Add Sankhofa Express
    create_or_update_transporter(
        email='express.africa@sankhofa.com',
        first_name='Sankhofa',
        last_name='Express',
        business_name='Sankhofa Express',
        vehicle_type='VAN',
        coverage_area='Abidjan, Dakar, Bamako, Cotonou, Lomé',
        phone_number='+225 07 00 00 02'
    )
    
    # 3. Add Sahel Transports
    create_or_update_transporter(
        email='trans.sahel@sankhofa.com',
        first_name='Sahel',
        last_name='Transports',
        business_name='Sahel Transports',
        vehicle_type='TRUCK',
        coverage_area='Ouagadougou, Niamey, Bamako',
        phone_number='+226 75 00 00 03'
    )
    
    # 4. Add Fara Delivery
    create_or_update_transporter(
        email='fara.delivery@sankhofa.com',
        first_name='Fara',
        last_name='Delivery',
        business_name='Fara Delivery',
        vehicle_type='MOTORCYCLE',
        coverage_area='Abidjan, Yamoussoukro',
        phone_number='+225 05 00 00 04'
    )
    
    print("Done seeding transporters.")
