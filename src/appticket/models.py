"""App ticket models.

Copyright (c) 2026 Aleksey Pavlov, ProjectSupport LLC.
email: a.pavlov@projectsupport.ru
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from mixins.models import BaseModel


class Status(models.TextChoices):
    """Ticket status."""

    NEW = "new", _("New")
    ACTIVE = "active", _("In progress")
    CLOSED = "closed", _("Closed")
    ARCHIVE = "archived", _("Archived")


class Ticket(BaseModel):
    """Ticket model."""

    number = models.PositiveBigIntegerField(
        editable=False,
        verbose_name=_("Number"),
        help_text=_("Ticket number"),
    )
    title = models.CharField(
        editable=False,
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("Briefly about the main thing"),
    )
    status = models.CharField(
        max_length=10,
        choices=Status,
        default=Status.NEW,
        verbose_name=_("Status"),
        help_text=_("Current ticket status"),
    )
    # другие поля...

    class Meta:
        """Metadata."""

        verbose_name = _("Ticket")
        verbose_name_plural = _("All tickets")


class NewTicket(Ticket):
    """New ticket proxy model."""

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = _("New ticket")
        verbose_name_plural = _("New")


class ActiveTicket(Ticket):
    """Active ticket proxy model."""

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = _("Ticket in progress")
        verbose_name_plural = _("In progress")


class ClosedTicket(Ticket):
    """Closed ticket."""

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = _("Closed ticket")
        verbose_name_plural = _("Closed")


class ArchivedTicket(Ticket):
    """Archived ticket proxy model."""

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = _("Archived ticket")
        verbose_name_plural = _("Archived")
