"""App queue configuration.

Copyright (c) 2026 Aleksey Pavlov, ProjectSupport LLC.
email: a.pavlov@projectsupport.ru
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppqueueConfig(AppConfig):
    """App queue configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appqueue'

    def ready(self) -> None:
        """Post-Initialization Setup."""
        self.verbose_name = _("Queue")
