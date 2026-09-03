import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings


def send_brevo_email(to_email, subject, html_content, to_name=None):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email, "name": to_name or to_email}],
        sender={"email": settings.DEFAULT_FROM_EMAIL, "name": "Sankofa"},
        subject=subject,
        html_content=html_content,
    )

    try:
        response = api_instance.send_transac_email(email)
        return response
    except ApiException as e:
        print(f"Erreur envoi email Brevo: {e}")
        raise