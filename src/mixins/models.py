"""Model mixins.

Copyright (c) 2026 Aleksey Pavlov, ProjectSupport LLC.
email: a.pavlov@projectsupport.ru
"""

from uuid import uuid4
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Абстракная базовая модель.

    Другие модели приложения должны наследоваться от этой модели.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name=_("ID"),
        help_text=_("Уникальный идентификатор"),
    )
    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Создан"),
        help_text=_("Дата создания"),
    )
    updated = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_("Изменен"),
        help_text=_("Дата последнего изменения"),
    )

    class Meta:
        abstract = True

    objects = models.Manager()
