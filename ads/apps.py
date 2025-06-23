from django.apps import AppConfig


class AdsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ads'

    def ready(self):
        try:
            import ads.templatetags.ads_extras  # noqa
        except ImportError:
            pass
