from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.common"
    verbose_name = "Common"

    def ready(self) -> None:
        import backend.apps.common.checks  # noqa: F401
        import backend.apps.common.signals  # noqa: F401
