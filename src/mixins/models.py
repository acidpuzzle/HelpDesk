"""Model mixins.

Copyright (c) 2026 Aleksey Pavlov, ProjectSupport LLC.
email: a.pavlov@projectsupport.ru
"""

from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Абстракная базовая модель.

    Другие модели приложения должны наследоваться от этой модели.
    """

    created: datetime = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Создан"),
        help_text=_("Дата создания"),
    )
    updated: datetime = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_("Изменен"),
        help_text=_("Дата последнего изменения"),
    )

    objects = models.Manager()

    class Meta:
        """Metaclass."""

        abstract = True
