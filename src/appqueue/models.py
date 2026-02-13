"""App queue models.

Copyright (c) 2026 Aleksey Pavlov, ProjectSupport LLC.
email: a.pavlov@projectsupport.ru
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from mixins.models import BaseModel


class Queue(BaseModel):
    """Queue model."""

    class Meta:
        """Metadata."""

        verbose_name = _("Queue")
        verbose_name_plural = _("Queues")