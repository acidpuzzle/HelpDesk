"""App ticket inlines.

Copyright (c) 2026 Aleksey Pavlov, ProjectSupport LLC.
email: a.pavlov@projectsupport.ru
"""

from django.contrib.admin import StackedInline
from django.forms import ModelForm

from appticket.models import Event


class EventInlineForm(ModelForm):
    class Meta:
        model = Event
        fields = ("type", "title", "comment")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            for field_name in ["type", "title", "comment"]:
                if field_name in self.fields:
                    self.fields[field_name].widget.attrs["readonly"] = True
                    self.fields[field_name].disabled = True


class EventStacked(StackedInline):
    """Result inline."""

    model = Event
    form = EventInlineForm
    extra = 0


    readonly_fields_exist = (
        "type",
        "title",
        "comment",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "type",
                    "title",
                    "comment",
                ),
            },
        ),
    )

    def has_delete_permission(self, _request, _obj=None) -> bool:
        """Cannot be deleted."""
        return False

    def has_add_permission(self, request, obj):
        if obj.is_closed() or obj.is_archived():
            return False
        return True
