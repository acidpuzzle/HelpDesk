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


class TicketQueue(BaseModel):
    """Очередь обращений."""

    name: str = models.CharField(
        max_length=255,
        verbose_name=_("Название"),
        help_text=_("Название очереди."),
    )


class Ticket(BaseModel):
    """Модель обращения."""

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

    class Category(models.TextChoices):
        """Катигории инцидентов."""

        INCIDENT = "incident", _("Инцидент")
        SERVICE = "service", _("Запрос на обслуживание")
        CHANGE = "change", _("Запрос на изменение")

    category: str = models.CharField(
        max_length=10,
        blank=True,
        choices=Category,
        default=Category.SERVICE,
        verbose_name=_("Категория"),
        help_text=_("Категория обращения"),
    )

    class Status(models.TextChoices):
        """Статус обращения."""

        NEW = "new", _("Новый")
        ASSIGNED = "assigned", _("Назначено")
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
    initiator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="init_tickets",
        verbose_name=_("Инициатор"),
        help_text=_("Инициатор обращения."),
    )
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="execute_tickets",
        verbose_name=_("Исполнитель"),
        help_text=_("Назначить на пользователя"),
    )
    detail = models.TextField(
        blank=True,
        verbose_name=_("Подробно"),
        help_text=_("Суть проблемы"),
    )

    class Meta:
        """Metadata."""

        verbose_name = _("Обращение")
        verbose_name_plural = _("Обращения")

    def save(self, *args, **kwargs) -> None:
        """Сохранение обращения."""
        if self.is_adding:
            with transaction.atomic():
                if not self.created:
                    self.created = timezone.now()

                today = self.created.date()
                date_prefix_int = int(self.created.strftime("%y%m%d")) * 1000

                max_number = (
                    Ticket.objects.select_for_update()
                    .filter(created__date=today)
                    .aggregate(max_num=Max("number"))["max_num"]
                )

                self.number = max_number + 1 if max_number else date_prefix_int + 1

                super().save(*args, **kwargs)

        if self.status == self.Status.NEW and self.executor:
            self.status = self.Status.ACTIVE

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
        verbose_name_plural = _("Новые")


class ActiveTicket(Ticket):
    """Active ticket proxy model."""

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = _("Обращение в работе")
        verbose_name_plural = _("В работе")


class PausedTicket(Ticket):
    """Paused ticket proxy model."""

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = _("Приостановленное обращение")
        verbose_name_plural = _("Приостановленные")


class ClosedTicket(Ticket):
    """Closed ticket."""

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = _("Закрытое обращение")
        verbose_name_plural = _("Закрытые")


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
        verbose_name=_("Пользователь"),
    )

    class EventType(models.TextChoices):
        """Тип события."""

        COMMENT = "comment", _("Коментарий")
        CALL = "call", _("Звонок клиенту")
        PAUSE = "pause", _("Приостановить")
        ACTIVE = "active", _("В работу")
        CLOSE = "close", _("Закрыть")

    type: str = models.CharField(
        choices=EventType,
        default=EventType.COMMENT,
        verbose_name=_("Тип события"),
        help_text=_("Выберите тип события"),
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

    def save(self, *args, **kwargs) -> None:
        if self.type == self.EventType.CLOSE:
            self.ticket.status = Ticket.Status.CLOSED
            self.ticket.save()
        elif self.type == self.EventType.PAUSE:
            self.ticket.status = Ticket.Status.PAUSED
            self.ticket.save()
        elif self.type == self.EventType.ACTIVE:
            self.ticket.status = Ticket.Status.ACTIVE
            self.ticket.save()

        super().save(*args, **kwargs)
