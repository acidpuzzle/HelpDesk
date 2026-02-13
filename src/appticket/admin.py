"""App ticket admin.

Copyright (c) 2026 Aleksey Pavlov, ProjectSupport LLC.
email: a.pavlov@projectsupport.ru
"""

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from appticket.models import (
    ActiveTicket,
    ArchivedTicket,
    ClosedTicket,
    NewTicket,
    Status,
)


@admin.register(NewTicket)
class NewTicketAdmin(admin.ModelAdmin):
    """New tickets."""

    def get_queryset(self, request: HttpRequest) -> QuerySet[NewTicket]:
        """Return new."""
        return super().get_queryset(request).filter(status=Status.NEW)


@admin.register(ActiveTicket)
class ActiveTicketAdmin(admin.ModelAdmin):
    """Active tickets."""

    def get_queryset(self, request: HttpRequest) -> QuerySet[ActiveTicket]:
        """Return active."""
        return super().get_queryset(request).filter(status=Status.ACTIVE)


@admin.register(ClosedTicket)
class ClosedTicketAdmin(admin.ModelAdmin):
    """Closed tickets."""

    def get_queryset(self, request: HttpRequest) -> QuerySet[ClosedTicket]:
        """Return closed."""
        return super().get_queryset(request).filter(status=Status.CLOSED)


@admin.register(ArchivedTicket)
class ArchivedTicketAdmin(admin.ModelAdmin):
    """Archived tickets."""

    def get_queryset(self, request: HttpRequest) -> QuerySet[ArchivedTicket]:
        """Return archived."""
        return super().get_queryset(request).filter(status=Status.ARCHIVE)
