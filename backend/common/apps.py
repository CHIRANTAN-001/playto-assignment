import sys
from django.apps import AppConfig

class CommonConfig(AppConfig):
    name = "common"
    def ready(self):
        # skip for management commands like migrate, makemigrations, shell
        if any(cmd in sys.argv for cmd in ["migrate", "makemigrations", "collectstatic", "shell"]):
            return

        from .startup import check_dependencies
        check_dependencies()