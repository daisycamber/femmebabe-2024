from django.apps import AppConfig

class VerifyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'verify'

    def ready(self):
        # Makes sure all signal handlers are connected
        from verify import handlers  # noqa
