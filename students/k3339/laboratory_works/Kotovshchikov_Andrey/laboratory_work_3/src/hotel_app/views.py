import calendar
from datetime import date
from django.db.models import (
    Prefetch,
    Count,
    Sum,
    Q,
    F,
    ExpressionWrapper,
    fields,
    functions,
)

from django.utils import timezone
from django.db import transaction
from django.db import connection

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from hotel_app import queries
from hotel_app.filters import IsRoomAvailableFilterBackend
from hotel_app.models import Booking, Employee, Floor, Guest, Room, Schedule
from hotel_app.serializers import (
    EmployeeDetailSerializer,
    EmployeeSerializer,
    GuestDetailSerializer,
    GuestSerializer,
    RoomBookingSerializer,
    RoomSerializer,
    ScheduleCreateSerializer,
)

from hotel_project.exceptions import Conflict, BadRequest


class EmployeePagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(
            data={
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "employees": data,
            }
        )


class EmployeeView(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer
    pagination_class = EmployeePagination
    queryset = Employee.objects.all().order_by("hire_date")


class EmployeeDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = EmployeeDetailSerializer
    queryset = (
        Employee.objects.prefetch_related(
            Prefetch(
                "schedule",
                queryset=Schedule.objects.select_related("floor")
                .all()
                .only("week_day", "floor__number"),
            )
        )
        .all()
        .order_by("hire_date")
    )


class EmployeeScheduleCreateView(generics.CreateAPIView):
    serializer_class = ScheduleCreateSerializer

    def perform_create(self, serializer):
        week_day = serializer.validated_data["week_day"]
        floor_number = serializer.validated_data["floor"]

        employee = generics.get_object_or_404(Employee, id=self.kwargs["employee_pk"])
        if employee.schedule.filter(week_day=week_day).exists():
            raise Conflict("Обнаружено пересечение в расписании")

        floor = Floor.objects.filter(number=floor_number).first()
        if floor is None:
            raise BadRequest("Этаж с таким номером не существует")

        Schedule.objects.create(
            employee=employee,
            floor=floor,
            week_day=week_day,
        )


class EmployeeScheduleResetView(APIView):
    def delete(self, request: Request, **kwargs):
        employee = generics.get_object_or_404(Employee, id=kwargs["employee_pk"])
        employee.schedule.all().delete()
        return Response(data={"success": "Расписание работника сброшено"})


class GuestPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(
            data={
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "guests": data,
            }
        )


class GuestView(generics.ListCreateAPIView):
    serializer_class = GuestSerializer
    pagination_class = GuestPagination
    queryset = Guest.objects.all()


class GuestDetailView(generics.RetrieveAPIView):
    serializer_class = GuestDetailSerializer
    queryset = (
        Guest.objects.prefetch_related(
            Prefetch(
                "booking",
                queryset=Booking.objects.select_related(
                    "room",
                    "room__floor",
                    "room__room_type",
                )
                .all()
                .order_by("-check_in_date"),
            )
        )
        .all()
        .order_by("id")
    )


class RoomView(generics.ListAPIView):
    serializer_class = RoomSerializer
    queryset = Room.objects.select_related("room_type", "floor").all()
    filter_backends = [IsRoomAvailableFilterBackend]


class RoomBookingView(APIView):
    @transaction.atomic
    def post(self, request: Request, **kwargs):
        serializer = RoomBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        guest = Guest.objects.filter(
            passport=serializer.validated_data["guest_passport"]
        ).first()

        if guest is None:
            raise BadRequest("Гость с таким паспортом не найден")

        room = generics.get_object_or_404(
            Room.objects.select_for_update(no_key=True),
            id=kwargs["pk"],
        )

        is_room_available = not (
            Booking.objects.filter(
                room=room,
                check_out_date__gte=timezone.now().strftime("%Y-%m-%d"),
            ).exists()
        )

        if not is_room_available:
            raise Conflict("Гостиничный номер занят")

        Booking.objects.create(
            room=room,
            guest=guest,
            check_out_date=serializer.validated_data["check_out_date"],
        )

        return Response(data={"success": "Номер успешно забронирован"})

    # def put(self, request: Request, **kwargs): ...


# {"guest_passport": "9999 999999", "check_out_date": "2024-11-16"}


class ReportPerQuarterView(APIView):
    def get(self, request: Request, **kwargs):
        quarter = self.kwargs["quarter"]
        if not (1 <= quarter <= 4):
            raise BadRequest("Квартал должен принимать значения от 1 до 4 включительно")

        current_year = timezone.now().year
        quarter_start_month = 3 * (quarter - 1) + 1
        quarter_end_month = 3 * quarter

        quarter_start = date(
            year=current_year,
            month=quarter_start_month,
            day=1,
        )

        quarter_end = date(
            year=current_year,
            month=quarter_end_month,
            day=calendar.monthrange(current_year, quarter_end_month)[1],
        )

        report = {
            "guest_count": self._count_quests(quarter_start, quarter_end),
            "room_count_per_floor": self._get_room_count_per_floor(),
            "profit_per_room": self._get_profit_per_room(quarter_start, quarter_end),
            "total_profit": self._calculate_total_profit(quarter_start, quarter_end),
        }

        return Response(data=report)

    def _count_quests(
        self,
        quarter_start: date,
        quarter_end: date,
    ) -> int:
        return Booking.objects.filter(
            check_in_date__gte=quarter_start.strftime("%Y-%m-%d"),
            check_out_date__lte=quarter_end.strftime("%Y-%m-%d"),
        ).aggregate(result=Count("id"))["result"]

    def _get_room_count_per_floor(self) -> dict:
        room_count_per_floor = dict()
        for floor in Floor.objects.annotate(room_count=Count("rooms")):
            room_count_per_floor[floor.number] = floor.room_count

        return room_count_per_floor

    def _get_profit_per_room(
        self,
        quarter_start: date,
        quarter_end: date,
    ) -> dict:
        profit_per_room = dict()
        with connection.cursor() as cursor:
            cursor.execute(
                queries.SELECT_PROFIT_PER_ROOM_FOR_QUARTER,
                {
                    "quarter_start": quarter_start.strftime("%Y-%m-%d"),
                    "quarter_end": quarter_end.strftime("%Y-%m-%d"),
                },
            )

            rows = cursor.fetchall()
            for row in rows:
                profit_per_room[row[1]] = row[2]

        return profit_per_room

    def _calculate_total_profit(
        self,
        quarter_start: date,
        quarter_end: date,
    ) -> int:
        return (
            Booking.objects.filter(
                check_in_date__gte=quarter_start.strftime("%Y-%m-%d"),
                check_out_date__lte=quarter_end.strftime("%Y-%m-%d"),
            )
            .values("room")
            .annotate(
                profit=ExpressionWrapper(
                    functions.ExtractDay(F("check_out_date") - F("check_in_date"))
                    * F("room__room_type__price_per_day"),
                    output_field=fields.DecimalField(),
                ),
            )
        ).aggregate(result=Sum("profit"))["result"]
