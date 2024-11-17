from django.utils import timezone
from django.db.models import Exists
from rest_framework import filters

from hotel_app.models import Room


class IsRoomAvailableFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        available_param = request.query_params.get("available")
        if (available_param is None) or available_param.lower() != "true":
            return queryset

        return queryset.filter(
            ~Exists(
                queryset.filter(
                    booking__check_out_date__gt=timezone.now().strftime("%Y-%m-%d")
                )
            )
        )
