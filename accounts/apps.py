from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    # def ready(self):
    #     # Importation des signaux au démarrage de l'application
    #     import accounts.signals
