from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from utils.email import send_brevo_email
from django.conf import settings
User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'id_card', 'is_verified', 'business_name', 'vehicle_type', 'coverage_area', 'address', 'country')
        read_only_fields = ('is_verified',)

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'profile')
        read_only_fields = ('id', 'role')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile

        # Update User fields
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        # Update Profile fields
        profile.phone_number = profile_data.get('phone_number', profile.phone_number)
        profile.address = profile_data.get('address', profile.address)
        profile.country = profile_data.get('country', profile.country)
        profile.business_name = profile_data.get('business_name', profile.business_name)
        profile.vehicle_type = profile_data.get('vehicle_type', profile.vehicle_type)
        profile.coverage_area = profile_data.get('coverage_area', profile.coverage_area)
        profile.save()

        return instance

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Les mots de passe ne correspondent pas."})
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    # Profile fields (to be passed during registration)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    id_card = serializers.FileField(required=False, allow_null=True, write_only=True)
    business_name = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    vehicle_type = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)
    coverage_area = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'role', 
                  'phone_number', 'id_card', 'business_name', 'vehicle_type', 'coverage_area')

    def create(self, validated_data):
        profile_data = {
            'phone_number': validated_data.pop('phone_number', None),
            'id_card': validated_data.pop('id_card', None),
            'business_name': validated_data.pop('business_name', None),
            'vehicle_type': validated_data.pop('vehicle_type', None),
            'coverage_area': validated_data.pop('coverage_area', None),
        }
        
        password = validated_data.pop('password')
        # L'utilisateur sera créé avec is_active=False
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        UserProfile.objects.create(user=user, **profile_data)
        
        # Envoi de l'e-mail d'activation
        self.send_activation_email(user)
        
        return user

    def send_activation_email(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # URL d'activation pointant vers le frontend
        activation_link = f"{settings.FRONTEND_URL}/activate/{uid}/{token}"
        
        subject = "Activez votre compte SANKHOFA 🚀"
        
        # Version Texte Brut (Fallback pour la compatibilité)
        text_message = (
            f"Bonjour {user.get_short_name()},\n\n"
            f"Bienvenue sur SANKHOFA !\n\n"
            f"Veuillez activer votre compte en copiant ce lien dans votre navigateur :\n"
            f"{activation_link}\n\n"
            f"Ce lien expirera dans 24 heures."
        )
        
        # Version HTML Soignée et Responsive
        html_message = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Activation de votre compte</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f4f6f9; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
          <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f6f9; padding: 40px 0;">
            <tr>
              <td align="center">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
                  
                  <!-- En-tête / Header -->
                  <tr>
                    <td align="center" style="background-color: #0F172A; padding: 36px 20px; color: #ffffff;">
                      <h1 style="margin: 0; font-size: 28px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; color: #F59E0B;">SANKHOFA</h1>
                    </td>
                  </tr>

                  <!-- Contenu Principal -->
                  <tr>
                    <td style="padding: 40px 30px;">
                      <h2 style="margin: 0 0 16px 0; font-size: 22px; color: #1E293B; font-weight: 700;">
                        Bienvenue, {user.get_short_name()} ! 👋
                      </h2>
                      <p style="margin: 0 0 24px 0; font-size: 15px; line-height: 1.6; color: #475569;">
                        Merci de vous être inscrit sur <strong>SANKHOFA</strong>. Pour finaliser la création de votre compte et accéder à nos services, veuillez confirmer votre adresse e-mail en cliquant sur le bouton ci-dessous.
                      </p>

                      <!-- Bouton Call To Action -->
                      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin: 32px 0;">
                        <tr>
                          <td align="center">
                            <a href="{activation_link}" target="_blank" style="display: inline-block; background-color: #2563EB; color: #ffffff; font-size: 16px; font-weight: 600; text-decoration: none; padding: 14px 32px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);">
                              Activer mon compte
                            </a>
                          </td>
                        </tr>
                      </table>

                      <p style="margin: 0 0 16px 0; font-size: 13px; line-height: 1.5; color: #64748B;">
                        ⏱️ Ce lien est valable pendant <strong>24 heures</strong>.
                      </p>
                      
                      <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 30px 0;" />

                      <p style="margin: 0; font-size: 12px; line-height: 1.5; color: #94A3B8;">
                        Si le bouton ne fonctionne pas, copiez-collez l'URL suivante dans votre navigateur :<br/>
                        <a href="{activation_link}" style="color: #2563EB; word-break: break-all;">{activation_link}</a>
                      </p>
                    </td>
                  </tr>

                  <!-- Pied de page / Footer -->
                  <tr>
                    <td align="center" style="background-color: #F8FAFC; padding: 24px 20px; border-top: 1px solid #E2E8F0;">
                      <p style="margin: 0; font-size: 12px; color: #94A3B8;">
                        Si vous n'avez pas créé de compte SANKHOFA, vous pouvez ignorer cet e-mail.
                      </p>
                      <p style="margin: 8px 0 0 0; font-size: 12px; color: #94A3B8;">
                        &copy; SANKHOFA. Tous droits réservés.
                      </p>
                    </td>
                  </tr>

                </table>
              </td>
            </tr>
          </table>
        </body>
        </html>
        """

        try:
            send_brevo_email(
                to_email=user.email,
                subject=subject,
                html_content=html_message,
                to_name=user.get_short_name(),
            )
        except Exception as e:
            print(f"⚠️ Erreur lors de l'envoi de l'e-mail d'activation : {e}")


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Les mots de passe ne correspondent pas."})
        return data
    
          
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
    
#     # Profile fields (to be passed during registration)
#     phone_number = serializers.CharField(required=False, write_only=True)
#     id_card = serializers.FileField(required=False, write_only=True)
#     business_name = serializers.CharField(required=False, write_only=True)
#     vehicle_type = serializers.CharField(required=False, write_only=True)
#     coverage_area = serializers.CharField(required=False, write_only=True)

#     class Meta:
#         model = User
#         fields = ('email', 'password', 'first_name', 'last_name', 'role', 
#                   'phone_number', 'id_card', 'business_name', 'vehicle_type', 'coverage_area')

#     def create(self, validated_data):
#         # Extract profile data
#         profile_data = {
#             'phone_number': validated_data.pop('phone_number', None),
#             'id_card': validated_data.pop('id_card', None),
#             'business_name': validated_data.pop('business_name', None),
#             'vehicle_type': validated_data.pop('vehicle_type', None),
#             'coverage_area': validated_data.pop('coverage_area', None),
#         }
        
#         # Create user
#         password = validated_data.pop('password')
#         user = User.objects.create_user(**validated_data)
#         user.set_password(password)
#         user.save()
        
#         # Create profile (profile is created automatically if using signals, but here we do it explicitly or update it)
#         UserProfile.objects.create(user=user, **profile_data)
        
#         return user
