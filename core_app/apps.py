from django.apps import AppConfig

class CoreAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_app'

    def ready(self):
        # هذا الاستيراد النسبي يضمن تحميل الـ signals
        from . import signals
