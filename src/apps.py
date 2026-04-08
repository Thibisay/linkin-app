from django.apps import AppConfig

class SrcConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import src.signals