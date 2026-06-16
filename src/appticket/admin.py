"""App ticket admin.

Copyright (c) 2026 Aleksey Pavlov, ProjectSupport LLC.
email: a.pavlov@projectsupport.ru
"""

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils import timezone

from appticket.inlines import EventStacked
from appticket.models import (
    ActiveTicket,
    ArchivedTicket,
    ClosedTicket,
    Event,
    NewTicket,
    Ticket, PausedTicket,
)


class TicketAdminForm(ModelForm):
    """Форма для обращения."""

    frozen_fields = (
        "title",
        "detail",
        "status",
    )

    class Meta:
        model = Ticket
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and not self.instance.is_adding():
            for field_name in self.frozen_fields:
                if field_name in self.fields:
                    self.fields[field_name].widget.attrs["readonly"] = True
                    self.fields[field_name].disabled = True


class TicketAdmin(admin.ModelAdmin):
    """Абстрактная админка, абстрактного обращения."""

    ticket_status: str
    form = TicketAdminForm
    inlines = (EventStacked,)

    list_display = (
        "number",
        "title",
        "status",
        "executor",
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[NewTicket]:
        """Переопределение родительского метода, фильтрация по статусу обращения."""
        return super().get_queryset(request).filter(status=self.ticket_status)

    def has_add_permission(self, request) -> bool:
        """Разрешить добавление обращений только в разделе новых обращений."""
        return self.ticket_status == Ticket.Status.NEW

    def has_delete_permission(self, request, obj=None) -> bool:
        """Не нужно удалять обращения."""
        return False

    def get_inlines(self, request, obj):
        if obj:
            return self.inlines
        return ()

    def save_formset(self, request, form, formset, change) -> None:
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, Event) and not instance.user:
                instance.user = request.user

            instance.save()
        formset.save_m2m()

    creation_fields = (
        "title",
        "detail",
    )

    def get_fields(self, request, obj=None):
        """Динамически определяет список полей в зависимости от создания/редактирования."""
        if obj is None:
            return self.creation_fields
        return super().get_fields(request, obj)


@admin.register(NewTicket)
class NewTicketAdmin(TicketAdmin):
    """New tickets."""

    ticket_status = Ticket.Status.NEW

    @admin.action(description="В работу")
    def activate(self, request, queryset) -> None:
        queryset.update(executor=request.user ,status=Ticket.Status.ACTIVE)
        self.message_user(request, "Обращения взяты в работу.")

    actions = [activate]


@admin.register(ActiveTicket)
class ActiveTicketAdmin(TicketAdmin):
    """Active tickets."""

    ticket_status = Ticket.Status.ACTIVE

    @admin.action(description="Приостановить")
    def pause(self, request, queryset) -> None:
        queryset.update(status=Ticket.Status.PAUSED)
        self.message_user(request, "Обращения успешно приостановленны.")

    actions = [pause]


@admin.register(PausedTicket)
class PausedTicketAdmin(TicketAdmin):
    """Active tickets."""

    ticket_status = Ticket.Status.PAUSED

    @admin.action(description="В работу")
    def activate(self, request, queryset) -> None:
        queryset.update(status=Ticket.Status.ACTIVE)
        self.message_user(request, "Обращения успешно возвращены в работу.")

    actions = [activate]


@admin.register(ClosedTicket)
class ClosedTicketAdmin(TicketAdmin):
    """Closed tickets."""

    ticket_status = Ticket.Status.CLOSED

    @admin.action(description="Архивировать")
    def archive(self, request, queryset) -> None:
        queryset.update(status=Ticket.Status.ARCHIVED)
        self.message_user(request, "Обращения успешно перемещены в архив.")

    actions = [archive]


@admin.register(ArchivedTicket)
class ArchivedTicketAdmin(TicketAdmin):
    """Archived tickets."""

    ticket_status = Ticket.Status.ARCHIVED
