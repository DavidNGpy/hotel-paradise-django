from django.contrib import admin
from .models import Habitacion, Cliente, Reservacion


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'precio_noche', 'capacidad', 'disponible')
    list_filter = ('tipo', 'disponible')
    search_fields = ('numero', 'tipo')
    ordering = ('numero',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'correo', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'apellidos', 'correo', 'telefono')
    readonly_fields = ('fecha_registro',)


@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'habitacion', 'fecha_entrada', 'fecha_salida', 'total', 'estado')
    list_filter = ('estado', 'fecha_entrada', 'habitacion__tipo')
    search_fields = ('cliente__nombre', 'cliente__apellidos', 'habitacion__numero')
    readonly_fields = ('total',)