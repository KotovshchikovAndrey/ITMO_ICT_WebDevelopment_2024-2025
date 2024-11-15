from rest_framework import serializers

from hotel_app.models import Booking, Employee, Guest, Room, RoomType, Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    week_day = serializers.CharField(source="get_week_day_display", read_only=True)
    floor = serializers.IntegerField(source="floor.number", read_only=True)

    class Meta:
        model = Schedule
        fields = ("week_day", "floor")


class ScheduleCreateSerializer(serializers.Serializer):
    week_day = serializers.ChoiceField(choices=Schedule.week_days)
    floor = serializers.IntegerField()


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        exclude = ("floors",)


class EmployeeDetailSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = (
            "id",
            "first_name",
            "last_name",
            "patronymic",
            "hire_date",
            "dismissal_date",
            "schedule",
        )

    def validate(self, data):
        if data["dismissal_date"] is None:
            return data

        if data["dismissal_date"] < data["hire_date"]:
            raise serializers.ValidationError(
                "дата увольнения не может быть меньше даты найма"
            )

        return data


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        exclude = ("rooms",)


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ("beds", "price_per_day")


class RoomSerializer(serializers.ModelSerializer):
    floor = serializers.CharField(source="floor.number")
    room_type = RoomTypeSerializer()

    class Meta:
        model = Room
        fields = (
            "id",
            "label",
            "phone",
            "floor",
            "room_type",
        )


class RoomBookingSerializer(serializers.Serializer):
    guest_passport = serializers.CharField()
    check_out_date = serializers.DateField()


class GuestBookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "check_in_date",
            "check_out_date",
            "room",
        )


class GuestDetailSerializer(serializers.ModelSerializer):
    booking = GuestBookingSerializer(many=True, read_only=True)

    class Meta:
        model = Guest
        fields = (
            "id",
            "first_name",
            "last_name",
            "patronymic",
            "passport",
            "city",
            "booking",
        )
