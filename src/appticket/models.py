"""App ticket models.

Copyright (c) 2026 Aleksey Pavlov, ProjectSupport LLC.
email: a.pavlov@projectsupport.ru
"""

from django.conf import settings
from django.db import models, transaction
from django.db.models import Max
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mixins.models import BaseModel


class Ticket(BaseModel):
    """Ticket model."""

    number: int = models.PositiveBigIntegerField(
        editable=False,
        verbose_name=_("Номер"),
        help_text=_("Номер обращения в системе"),
    )
    title: str = models.CharField(
        max_length=255,
        verbose_name=_("Название"),
        help_text=_("Коротко о главном"),
    )

    class Status(models.TextChoices):
        """Ticket status."""

        NEW = "new", _("Новый")
        ACTIVE = "active", _("В работе")
        PAUSED = "paused", _("Приостановлена")
        CLOSED = "closed", _("Закрыта")
        ARCHIVED = "archived", _("Архивиорована")

    status: Status = models.CharField(
        max_length=10,
        choices=Status,
        default=Status.NEW,
        verbose_name=_("Статус"),
        help_text=_("Статус обращения"),
    )
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="tickets",
        verbose_name = _("Исполнитель"),
        help_text = _("Назначить на пользователя"),
    )
    detail = models.TextField(
        blank=True,
        verbose_name=_("Подробно"),
        help_text=_("Суть проблемы"),
    )
    # другие поля...

    class Meta:
        """Metadata."""

        verbose_name = _("Обращение")
        verbose_name_plural = _("Обращения")


    def save(self, *args, **kwargs):
        if self._state.adding:
            if not self.created:
                self.created = timezone.now()

            today = self.created.date()

            date_prefix_str = self.created.strftime("%y%m%d")
            date_prefix_int = int(date_prefix_str) * 1000

            with transaction.atomic():
                max_number = (
                    Ticket.objects.select_for_update()
                    .filter(created__date=today)
                    .aggregate(max_num=Max("number"))["max_num"]
                )

                if max_number:
                    self.number = max_number + 1
                else:
                    self.number = date_prefix_int + 1

                super().save(*args, **kwargs)
        elif self.status == self.Status.NEW and self.executor:
            self.status = self.Status.ACTIVE
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Обращение №{self.number} - {self.title}"

    def is_archived(self):
        return self.status == self.Status.ARCHIVED

    def is_closed(self):
        return self.status == self.Status.CLOSED


class NewTicket(Ticket):
    """New ticket proxy model."""

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = _("Новое обращение")
        verbose_name_plural = _("Новые обращения")


class ActiveTicket(Ticket):
    """Active ticket proxy model."""

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = _("Обращение в работе")
        verbose_name_plural = _("Обращения в работе")


class ClosedTicket(Ticket):
    """Closed ticket."""

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = _("Закрытое обращение")
        verbose_name_plural = _("Закрытые обращения")


class ArchivedTicket(Ticket):
    """Archived ticket proxy model."""

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = _("Архивное обращение")
        verbose_name_plural = _("Архивные обращения")


class Event(BaseModel):
    """Event model."""

    ticket = models.ForeignKey(
        Ticket,
        related_name="events",
        on_delete=models.CASCADE,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="events",
        verbose_name = _("Пользователь"),
    )

    class EventType(models.TextChoices):
        """Тип события."""

        COMMENT = "comment", _("Коментарий")
        CALL = "call", _("Звонок клиенту")
        PAUSE = "pause", _("Приостановить")
        CLOSE = "close", _("Закрыть")

    type: str = models.CharField(
        choices=EventType,
        default=EventType.COMMENT,
        verbose_name=_("Тип события"),
        help_text=_("Выберите тип события"),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("Заголовок"),
        help_text=_("Коротко о главном"),
    )
    comment = models.TextField(
        blank=False,
        verbose_name=_("Коментарий"),
        help_text=_("Прокоментируйте ваши действия."),
    )

    class Meta:
        """Metadata."""

        verbose_name = _("Событие")
        verbose_name_plural = _("События")

    def __str__(self):
        formatted_date = self.created.strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.user} от {formatted_date}"

    def save(self, *args, **kwargs):
        if self.type == self.EventType.CLOSE:
            self.ticket.status = Ticket.Status.CLOSED
            self.ticket.save()

        super().save(*args, **kwargs)

