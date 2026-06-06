"""App ticket admin.

Copyright (c) 2026 Aleksey Pavlov, ProjectSupport LLC.
email: a.pavlov@projectsupport.ru
"""

from django.contrib import admin
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest

from appticket.inlines import EventStacked
from appticket.models import (
    ActiveTicket,
    ArchivedTicket,
    ClosedTicket,
    Event,
    NewTicket,
    Ticket,
)


class TicketAdminForm(ModelForm):
    class Meta:
        model = Ticket
        fields = (
            "title",
            "detail",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            for field_name in ["title", "detail"]:
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

    # def get_readonly_fields(self, request, obj=None):
    #     """
    #     Hook for specifying custom readonly fields.
    #     """
    #     if obj:
    #         return self.readonly_fields_exist
    #     return self.readonly_fields_to_add
    #
    # def get_fields(self, request, obj=None):
    #     if obj:
    #         return self.fields_exist
    #     return self.fields_to_add

    def has_add_permission(self, request):
        """Разрешить добавление обращений только в разделе новых обращений.
        :param request:
        :return: Bool
        """
        if self.ticket_status == Ticket.Status.NEW:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_inlines(self, request, obj):
        if obj:
            return self.inlines
        return ()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, Event) and not instance.user:
                instance.user = request.user

            instance.save()
        formset.save_m2m()


@admin.register(NewTicket)
class NewTicketAdmin(TicketAdmin):
    """New tickets."""

    ticket_status = Ticket.Status.NEW


@admin.register(ActiveTicket)
class ActiveTicketAdmin(TicketAdmin):
    """Active tickets."""

    ticket_status = Ticket.Status.ACTIVE


@admin.register(ClosedTicket)
class ClosedTicketAdmin(TicketAdmin):
    """Closed tickets."""

    ticket_status = Ticket.Status.CLOSED


@admin.register(ArchivedTicket)
class ArchivedTicketAdmin(TicketAdmin):
    """Archived tickets."""

    ticket_status = Ticket.Status.ARCHIVED
