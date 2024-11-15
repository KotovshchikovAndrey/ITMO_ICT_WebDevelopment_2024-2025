from django.db.models import Prefetch
from django.utils import timezone
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

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
