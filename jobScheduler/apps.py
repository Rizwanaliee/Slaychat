from django.apps import AppConfig

class JobschedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobScheduler'

    def ready(self):
        from . import updater
        updater.start()
