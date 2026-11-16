from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Habitaciones
    path('habitaciones/', views.lista_habitaciones, name='lista_habitaciones'),
    path('habitaciones/nueva/', views.crear_habitacion, name='crear_habitacion'),
    path('habitaciones/editar/<int:pk>/', views.editar_habitacion, name='editar_habitacion'),
    path('habitaciones/eliminar/<int:pk>/', views.eliminar_habitacion, name='eliminar_habitacion'),

    # Clientes
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', views.crear_cliente, name='crear_cliente'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),

    # Reservaciones y Disponibilidad
    path('reservaciones/', views.lista_reservaciones, name='lista_reservaciones'),
    path('reservaciones/nueva/', views.crear_reservacion, name='crear_reservacion'),
    path('reservaciones/editar/<int:pk>/', views.editar_reservacion, name='editar_reservacion'),
    path('reservaciones/cancelar/<int:pk>/', views.cancelar_reservacion, name='cancelar_reservacion'),
    path('disponibilidad/', views.consultar_disponibilidad, name='consultar_disponibilidad'),

    # Reportes
    path('reportes/', views.reportes, name='reportes'),
]