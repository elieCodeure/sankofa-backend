import requests
from rest_framework import generics, permissions, status, response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from django.utils.encoding import force_str
from django.core.mail import send_mail
from django.conf import settings
from .serializers import PasswordResetConfirmSerializer, PasswordResetRequestSerializer, RegisterSerializer, UserSerializer, ChangePasswordSerializer

User = get_user_model()

class SankhofaTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        # Vérification si l'utilisateur existe et est actif
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return response.Response(
                    {"detail": "Votre compte n'est pas encore activé. Veuillez vérifier votre boîte mail."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except User.DoesNotExist:
            pass  # Laisse TokenObtainPairView gérer les identifiants invalides
            
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return response.Response({"detail": "Identifiants invalides"}, status=status.HTTP_401_UNAUTHORIZED)
            
        user = User.objects.get(email=email)
        refresh = RefreshToken.for_user(user)
        
        return response.Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Notification à l'admin pour les vendeurs et transporteurs
            if user.role in ['SELLER', 'TRANSPORTER']:
                self.notify_admin(user)
                
            return response.Response({
                'message': "Inscription réussie ! Un e-mail d'activation vous a été envoyé.",
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
            
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def notify_admin(self, user):
        subject = f"Nouveau dossier Sankhofa à valider : {user.role}"
        message = f"L'utilisateur {user.email} s'est inscrit en tant que {user.role}.\n" \
                  f"Veuillez vérifier ses documents d'identité dans l'interface d'administration."
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email to admin: {e}")

# VUE D'ACTIVATION DU COMPTE
class ActivateAccountView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if user.is_active:
                return response.Response(
                    {"message": "Votre compte est déjà activé. Vous pouvez vous connecter."},
                    status=status.HTTP_200_OK
                )
            user.is_active = True
            user.save()
            return response.Response(
                {"message": "Votre compte a été activé avec succès ! Vous pouvez maintenant vous connecter."},
                status=status.HTTP_200_OK
            )
        else:
            return response.Response(
                {"detail": "Le lien d'activation est invalide ou a expiré."},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        if not user.check_password(serializer.data.get("old_password")):
            return response.Response(
                {"old_password": ["Ancien mot de passe incorrect."]}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mise à jour du mot de passe
        user.set_password(serializer.data.get("new_password"))
        user.save()

        # Envoi de l'e-mail d'alerte de sécurité
        self.send_security_alert_email(user)

        return response.Response(
            {"detail": "Mot de passe mis à jour avec succès."}, 
            status=status.HTTP_200_OK
        )

    def send_security_alert_email(self, user):
        subject = "Alerte Sécurité : Modification de votre mot de passe - SANKHOFA 🛡️"
        
        text_message = (
            f"Bonjour {user.get_short_name()},\n\n"
            f"Nous vous confirmons que le mot de passe de votre compte SANKHOFA a été modifié avec succès.\n\n"
            f"Si vous êtes à l'origine de cette modification, vous pouvez ignorer cet e-mail.\n"
            f"Si vous n'avez pas effectué ce changement, veuillez contacter immédiatement notre support."
        )

        html_message = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #f4f6f9; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
          <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f6f9; padding: 40px 0;">
            <tr>
              <td align="center">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
                  
                  <!-- Header -->
                  <tr>
                    <td align="center" style="background-color: #0F172A; padding: 36px 20px;">
                      <h1 style="margin: 0; font-size: 28px; font-weight: 800; letter-spacing: 2px; color: #F59E0B;">SANKHOFA</h1>
                    </td>
                  </tr>

                  <!-- Body -->
                  <tr>
                    <td style="padding: 40px 30px;">
                      <h2 style="margin: 0 0 16px 0; font-size: 20px; color: #1E293B; font-weight: 700;">
                        Votre mot de passe a été modifié 🛡️
                      </h2>
                      <p style="margin: 0 0 16px 0; font-size: 15px; line-height: 1.6; color: #475569;">
                        Bonjour <strong>{user.get_short_name()}</strong>,
                      </p>
                      <p style="margin: 0 0 24px 0; font-size: 15px; line-height: 1.6; color: #475569;">
                        Nous vous confirmons que le mot de passe de votre compte SANKHOFA ({user.email}) vient d'être modifié avec succès.
                      </p>

                      <div style="background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 16px; border-radius: 4px; margin: 24px 0;">
                        <p style="margin: 0; font-size: 14px; color: #991B1B; line-height: 1.5;">
                          ⚠️ <strong>Vous n'êtes pas à l'origine de cette action ?</strong><br/>
                          Si vous n'avez pas modifié votre mot de passe, votre compte a peut-être été compromis. Veuillez réinitialiser votre mot de passe immédiatement ou contacter le support SANKHOFA.
                        </p>
                      </div>

                      <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 30px 0;" />

                      <p style="margin: 0; font-size: 12px; color: #94A3B8;">
                        Cet e-mail est une alerte de sécurité automatique relative à votre compte.
                      </p>
                    </td>
                  </tr>

                  <!-- Footer -->
                  <tr>
                    <td align="center" style="background-color: #F8FAFC; padding: 24px 20px; border-top: 1px solid #E2E8F0;">
                      <p style="margin: 0; font-size: 12px; color: #94A3B8;">&copy; SANKHOFA. Tous droits réservés.</p>
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
            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"⚠️ Erreur lors de l'envoi de l'alerte de sécurité : {e}")
    


# N'oublie pas d'importer tes nouveaux serializers depuis .serializers :
# PasswordResetRequestSerializer, PasswordResetConfirmSerializer

class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            self.send_reset_email(user)
        except User.DoesNotExist:
            # Pour des raisons de sécurité, on ne dévoile pas si l'e-mail existe ou non
            pass

        return response.Response({
            "detail": "Si cette adresse e-mail existe, un lien de réinitialisation vous a été envoyé."
        }, status=status.HTTP_200_OK)

    def send_reset_email(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # URL du frontend pour la réinitialisation
        reset_link = f"http://localhost:8081/reset-password/{uid}/{token}"

        subject = "Réinitialisation de votre mot de passe - SANKHOFA 🔒"
        
        text_message = (
            f"Bonjour {user.get_short_name()},\n\n"
            f"Vous avez demandé la réinitialisation de votre mot de passe SANKHOFA.\n"
            f"Veuillez utiliser ce lien pour définir un nouveau mot de passe :\n"
            f"{reset_link}\n\n"
            f"Ce lien expirera dans 24 heures.\n"
            f"Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet e-mail."
        )

        html_message = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; background-color: #f4f6f9; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
          <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f6f9; padding: 40px 0;">
            <tr>
              <td align="center">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
                  
                  <!-- Header -->
                  <tr>
                    <td align="center" style="background-color: #0F172A; padding: 36px 20px;">
                      <h1 style="margin: 0; font-size: 28px; font-weight: 800; letter-spacing: 2px; color: #F59E0B;">SANKHOFA</h1>
                    </td>
                  </tr>

                  <!-- Body -->
                  <tr>
                    <td style="padding: 40px 30px;">
                      <h2 style="margin: 0 0 16px 0; font-size: 20px; color: #1E293B; font-weight: 700;">
                        Réinitialisation de votre mot de passe 🔑
                      </h2>
                      <p style="margin: 0 0 24px 0; font-size: 15px; line-height: 1.6; color: #475569;">
                        Bonjour <strong>{user.get_short_name()}</strong>,<br/><br/>
                        Nous avons reçu une demande de réinitialisation du mot de passe pour votre compte SANKHOFA. Cliquez sur le bouton ci-dessous pour choisir un nouveau mot de passe.
                      </p>

                      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin: 32px 0;">
                        <tr>
                          <td align="center">
                            <a href="{reset_link}" target="_blank" style="display: inline-block; background-color: #DC2626; color: #ffffff; font-size: 16px; font-weight: 600; text-decoration: none; padding: 14px 32px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(220, 38, 38, 0.3);">
                              Réinitialiser mon mot de passe
                            </a>
                          </td>
                        </tr>
                      </table>

                      <p style="margin: 0 0 16px 0; font-size: 13px; color: #64748B;">
                        ⏱️ Ce lien est valable pendant <strong>24 heures</strong>.
                      </p>
                      
                      <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 30px 0;" />

                      <p style="margin: 0; font-size: 12px; color: #94A3B8;">
                        Si vous n'avez pas demandé ce changement, aucune action n'est requise. Votre mot de passe actuel reste inchangé.
                      </p>
                    </td>
                  </tr>

                  <!-- Footer -->
                  <tr>
                    <td align="center" style="background-color: #F8FAFC; padding: 24px 20px; border-top: 1px solid #E2E8F0;">
                      <p style="margin: 0; font-size: 12px; color: #94A3B8;">&copy; SANKHOFA. Tous droits réservés.</p>
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
            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"⚠️ Erreur lors de l'envoi du mail de réinitialisation : {e}")


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return response.Response({
                "detail": "Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter."
            }, status=status.HTTP_200_OK)
        
        return response.Response({
            "error": "Lien de réinitialisation invalide ou expiré."
        }, status=status.HTTP_400_BAD_REQUEST)

class GoogleLoginView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        if not token:
            return response.Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the token with Google using userinfo endpoint (since frontend uses access_token)
            res = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            if res.status_code != 200:
                return response.Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

            user_data = res.json()
            email = user_data.get('email')
            if not email:
                return response.Response({"error": "Email not provided by Google"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if user exists
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return response.Response({"error": "Aucun compte trouvé avec cet e-mail. Veuillez vous inscrire."}, status=status.HTTP_404_NOT_FOUND)

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            user_data_resp = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": getattr(user, 'role', 'CLIENT'),
                "profile": None
            }
            try:
                profile = getattr(user, 'profile')
                if profile:
                    user_data_resp["profile"] = {
                        "phone_number": getattr(profile, 'phone_number', ''),
                        "address": getattr(profile, 'address', ''),
                        "country": getattr(profile, 'country', ''),
                    }
            except Exception:
                pass
            
            return response.Response({
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "user": user_data_resp
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return response.Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GoogleRegisterView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        if not token:
            return response.Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the token with Google using userinfo endpoint
            res = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"}
            )
            if res.status_code != 200:
                return response.Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

            user_data = res.json()
            email = user_data.get('email')
            if not email:
                return response.Response({"error": "Email not provided by Google"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if user exists
            try:
                user = User.objects.get(email=email)
                return response.Response({"error": "Un compte avec cet e-mail existe déjà. Veuillez vous connecter."}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                # Create user
                first_name = user_data.get('given_name', '')
                last_name = user_data.get('family_name', '')
                requested_role = request.data.get('role', 'CLIENT')
                
                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                user.set_unusable_password()
                user.role = requested_role
                user.is_active = False
                user.save()

                from .models import UserProfile
                UserProfile.objects.create(user=user)

                # Send activation email using RegisterSerializer's method
                serializer = RegisterSerializer()
                serializer.send_activation_email(user)
                
                # Notification à l'admin pour les vendeurs et transporteurs
                if requested_role in ['SELLER', 'TRANSPORTER']:
                    # Re-use notify_admin from RegisterView?
                    # Or we can just import it or define it.
                    pass # We will use RegisterView().notify_admin(user)
                
                register_view = RegisterView()
                if requested_role in ['SELLER', 'TRANSPORTER']:
                    register_view.notify_admin(user)

            user_data_resp = UserSerializer(user).data
            
            return response.Response({
                'message': "Inscription Google réussie ! Un e-mail d'activation vous a été envoyé.",
                'user': user_data_resp
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return response.Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)