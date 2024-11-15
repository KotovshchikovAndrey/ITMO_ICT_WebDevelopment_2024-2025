from django.contrib import admin

from hotel_app.models import Floor, Room, RoomType


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin): ...


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin): ...


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin): ...
