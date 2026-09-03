# accounts/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile


# 1. pre_save : On garde en mémoire l'ancien état de "is_verified"
@receiver(pre_save, sender=UserProfile)
def track_verification_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = UserProfile.objects.get(pk=instance.pk)
            instance._old_is_verified = old_instance.is_verified
        except UserProfile.DoesNotExist:
            instance._old_is_verified = False
    else:
        instance._old_is_verified = False


# 2. post_save : Déclenche l'envoi d'e-mail uniquement si "is_verified" a changé
@receiver(post_save, sender=UserProfile)
def notify_provider_verification_status(sender, instance, created, **kwargs):
    user = instance.user

    # Filtre strict : Ne concerne QUE les prestataires (SELLER et TRANSPORTER)
    if user.role not in ['SELLER', 'TRANSPORTER']:
        return

    old_verified = getattr(instance, '_old_is_verified', False)
    new_verified = instance.is_verified

    # On n'envoie l'e-mail QUE si le statut a réellement basculé
    if old_verified != new_verified:
        if new_verified:
            send_verification_approved_email(user)
        else:
            send_verification_rejected_email(user)


def send_verification_approved_email(user):
    role_name = "Vendeur" if user.role == 'SELLER' else "Transporteur"
    subject = "Félicitations ! Votre compte prestataire a été vérifié - SANKHOFA 🎉"

    text_message = (
        f"Bonjour {user.get_short_name()},\n\n"
        f"Excellente nouvelle ! Vos documents d'identité ont été validés par notre équipe.\n"
        f"Votre profil {role_name} est désormais officiellement VÉRIFIÉ.\n\n"
        f"Vous pouvez dès à présent profiter de toutes les fonctionnalités sur SANKHOFA."
    )

    html_message = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head><meta charset="UTF-8"></head>
    <body style="margin: 0; padding: 0; background-color: #f4f6f9; font-family: Arial, sans-serif;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="padding: 40px 0;">
        <tr>
          <td align="center">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
              <tr>
                <td align="center" style="background-color: #0F172A; padding: 30px;">
                  <h1 style="margin: 0; color: #F59E0B; letter-spacing: 2px;">SANKHOFA</h1>
                </td>
              </tr>
              <tr>
                <td style="padding: 40px 30px;">
                  <span style="background-color: #DCFCE7; color: #166534; font-size: 12px; font-weight: bold; padding: 6px 12px; border-radius: 20px;">✓ PROFIL VÉRIFIÉ</span>
                  <h2 style="color: #1E293B; margin-top: 15px;">Votre compte {role_name} est validé ! 🚀</h2>
                  <p style="color: #475569; line-height: 1.6;">
                    Bonjour <strong>{user.get_short_name()}</strong>,<br/><br/>
                    Vos documents d'identité ont été examinés et <strong>approuvés</strong> par notre équipe.
                  </p>
                  <div style="background-color: #F8FAFC; border-left: 4px solid #10B981; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #065F46;">
                      Vous disposez désormais du badge de confiance et vous pouvez proposer vos services sur la plateforme sans restriction.
                    </p>
                  </div>
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
        print(f"⚠️ Erreur d'envoi du mail de validation : {e}")


def send_verification_rejected_email(user):
    role_name = "Vendeur" if user.role == 'SELLER' else "Transporteur"
    subject = "Mise à jour concernant la vérification de votre compte - SANKHOFA ⚠️"

    text_message = (
        f"Bonjour {user.get_short_name()},\n\n"
        f"Le statut de vérification de votre compte {role_name} a été révoqué ou non approuvé.\n"
        f"Veuillez vérifier vos documents d'identité dans votre espace profil."
    )

    html_message = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head><meta charset="UTF-8"></head>
    <body style="margin: 0; padding: 0; background-color: #f4f6f9; font-family: Arial, sans-serif;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="padding: 40px 0;">
        <tr>
          <td align="center">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
              <tr>
                <td align="center" style="background-color: #0F172A; padding: 30px;">
                  <h1 style="margin: 0; color: #F59E0B; letter-spacing: 2px;">SANKHOFA</h1>
                </td>
              </tr>
              <tr>
                <td style="padding: 40px 30px;">
                  <span style="background-color: #FEE2E2; color: #991B1B; font-size: 12px; font-weight: bold; padding: 6px 12px; border-radius: 20px;">⚠️ VÉRIFICATION NON VALIDÉE</span>
                  <h2 style="color: #1E293B; margin-top: 15px;">Mise à jour de votre compte {role_name}</h2>
                  <p style="color: #475569; line-height: 1.6;">
                    Bonjour <strong>{user.get_short_name()}</strong>,<br/><br/>
                    La vérification de votre profil n'a pas été validée ou a été temporairement révoquée par l'administration.
                  </p>
                  <div style="background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #991B1B;">
                      Vérifiez que votre pièce d'identité est lisible et valide, puis mettez à jour votre document sur votre profil.
                    </p>
                  </div>
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
        print(f"⚠️ Erreur d'envoi du mail de refus : {e}")