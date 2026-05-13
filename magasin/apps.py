from django.apps import AppConfig


class MagasinConfig(AppConfig):
    name = 'magasin'

    def ready(self):
        import magasin.signals
