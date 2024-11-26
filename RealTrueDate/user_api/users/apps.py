from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_api.users'

    def ready(self):
        import user_api.users.signals  # Import the signals module