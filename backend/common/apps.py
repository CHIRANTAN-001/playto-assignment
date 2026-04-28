import sys
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class CommonConfig(AppConfig):
    name = "common"
    def ready(self):
        # skip for management commands like migrate, makemigrations, shell
        if any(cmd in sys.argv for cmd in ["migrate", "makemigrations", "collectstatic", "shell"]):
            return

        from .startup import check_dependencies
        ok = check_dependencies()
        if not ok:
            logger.warning("Dependencies not met. Exiting...")