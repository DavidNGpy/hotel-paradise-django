from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Sum, Count
from .models import Habitacion, Cliente, Reservacion
from .forms import HabitacionForm, ClienteForm, ReservacionForm


# ==========================================
# AUTENTICACIÓN (LOGIN / LOGOUT)
# ==========================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido al sistema, {user.username}.")
            return redirect('dashboard')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, 'gestion/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login')


# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================
@login_required
def dashboard(request):
    total_clientes = Cliente.objects.count()
    total_habitaciones = Habitacion.objects.count()
    habitaciones_disponibles = Habitacion.objects.filter(disponible=True).count()
    total_reservaciones = Reservacion.objects.count()

    # Ingresos generados (Reservaciones Confirmadas o Completadas)
    ingresos_data = Reservacion.objects.filter(
        estado__in=['Confirmada', 'Completada']
    ).aggregate(total_ingresos=Sum('total'))
    ingresos_generados = ingresos_data['total_ingresos'] or 0

    ultimas_reservaciones = Reservacion.objects.select_related('cliente', 'habitacion')[:5]

    context = {
        'total_clientes': total_clientes,
        'total_habitaciones': total_habitaciones,
        'habitaciones_disponibles': habitaciones_disponibles,
        'total_reservaciones': total_reservaciones,
        'ingresos_generados': ingresos_generados,
        'ultimas_reservaciones': ultimas_reservaciones,
    }
    return render(request, 'gestion/dashboard.html', context)


# ==========================================
# MÓDULO HABITACIONES (CRUD + BÚSQUEDA)
# ==========================================
@login_required
def lista_habitaciones(request):
    query = request.GET.get('q', '')
    tipo_filtro = request.GET.get('tipo', '')
    habitaciones = Habitacion.objects.all()

    if query:
        habitaciones = habitaciones.filter(
            Q(numero__icontains=query) | Q(tipo__icontains=query)
        )
    if tipo_filtro:
        habitaciones = habitaciones.filter(tipo=tipo_filtro)

    context = {
        'habitaciones': habitaciones,
        'query': query,
        'tipo_filtro': tipo_filtro,
        'tipos': Habitacion.TIPOS_HABITACION,
    }
    return render(request, 'gestion/habitaciones_lista.html', context)


@login_required
def crear_habitacion(request):
    if request.method == 'POST':
        form = HabitacionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Habitación registrada correctamente.")
            return redirect('lista_habitaciones')
    else:
        form = HabitacionForm()
    return render(request, 'gestion/habitacion_form.html', {'form': form, 'titulo': 'Nueva Habitación'})


@login_required
def editar_habitacion(request, pk):
    habitacion = get_object_or_404(Habitacion, pk=pk)
    if request.method == 'POST':
        form = HabitacionForm(request.POST, request.FILES, instance=habitacion)
        if form.is_valid():
            form.save()
            messages.success(request, f"Habitación #{habitacion.numero} actualizada.")
            return redirect('lista_habitaciones')
    else:
        form = HabitacionForm(instance=habitacion)
    return render(request, 'gestion/habitacion_form.html', {
        'form': form,
        'titulo': f'Editar Habitación #{habitacion.numero}'
    })


@login_required
def eliminar_habitacion(request, pk):
    habitacion = get_object_or_404(Habitacion, pk=pk)
    if request.method == 'POST':
        # Regla 5: No se puede eliminar una habitación con reservaciones activas
        if habitacion.tiene_reservas_activas():
            messages.error(
                request,
                f"No se puede eliminar la Habitación #{habitacion.numero} porque tiene reservaciones activas."
            )
            return redirect('lista_habitaciones')
        try:
            habitacion.delete()
            messages.success(request, f"Habitación #{habitacion.numero} eliminada correctamente.")
        except Exception as e:
            messages.error(request, f"No se pudo eliminar la habitación: {e}")
        return redirect('lista_habitaciones')

    return render(request, 'gestion/confirmar_eliminar.html', {
        'objeto': f"Habitación #{habitacion.numero} ({habitacion.tipo})",
        'cancel_url': 'lista_habitaciones'
    })


# ==========================================
# MÓDULO CLIENTES (CRUD + BÚSQUEDA)
# ==========================================
@login_required
def lista_clientes(request):
    query = request.GET.get('q', '')
    clientes = Cliente.objects.all()
    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) |
            Q(apellidos__icontains=query) |
            Q(correo__icontains=query)
        )
    return render(request, 'gestion/clientes_lista.html', {'clientes': clientes, 'query': query})


@login_required
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente registrado exitosamente.")
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'gestion/cliente_form.html', {'form': form, 'titulo': 'Registrar Cliente'})


@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos del cliente actualizados.")
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'gestion/cliente_form.html', {
        'form': form,
        'titulo': f'Editar Cliente: {cliente.nombre} {cliente.apellidos}'
    })


@login_required
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, "Cliente eliminado del sistema.")
        return redirect('lista_clientes')
    return render(request, 'gestion/confirmar_eliminar.html', {
        'objeto': f"{cliente.nombre} {cliente.apellidos} ({cliente.correo})",
        'cancel_url': 'lista_clientes'
    })


# ==========================================
# MÓDULO RESERVACIONES (CRUD + CANCELAR + DISPONIBILIDAD)
# ==========================================
@login_required
def lista_reservaciones(request):
    query = request.GET.get('q', '')
    estado_filtro = request.GET.get('estado', '')
    reservaciones = Reservacion.objects.select_related('cliente', 'habitacion').all()

    if query:
        reservaciones = reservaciones.filter(
            Q(cliente__nombre__icontains=query) |
            Q(cliente__apellidos__icontains=query) |
            Q(habitacion__numero__icontains=query) |
            Q(habitacion__tipo__icontains=query)
        )
    if estado_filtro:
        reservaciones = reservaciones.filter(estado=estado_filtro)

    context = {
        'reservaciones': reservaciones,
        'query': query,
        'estado_filtro': estado_filtro,
        'estados': Reservacion.ESTADOS_RESERVACION,
    }
    return render(request, 'gestion/reservaciones_lista.html', context)


@login_required
def crear_reservacion(request):
    if request.method == 'POST':
        form = ReservacionForm(request.POST)
        if form.is_valid():
            reserva = form.save()
            messages.success(
                request,
                f"Reservación #{reserva.id} creada. Total calculado: ${reserva.total} MXN."
            )
            return redirect('lista_reservaciones')
    else:
        # Si viene preseleccionada una habitación desde Consulta de Disponibilidad
        initial = {}
        hab_id = request.GET.get('habitacion')
        entrada = request.GET.get('entrada')
        salida = request.GET.get('salida')
        if hab_id:
            initial['habitacion'] = hab_id
        if entrada:
            initial['fecha_entrada'] = entrada
        if salida:
            initial['fecha_salida'] = salida
        form = ReservacionForm(initial=initial)

    return render(request, 'gestion/reservacion_form.html', {
        'form': form,
        'titulo': 'Nueva Reservación'
    })


@login_required
def editar_reservacion(request, pk):
    reservacion = get_object_or_404(Reservacion, pk=pk)
    if request.method == 'POST':
        form = ReservacionForm(request.POST, instance=reservacion)
        if form.is_valid():
            reserva = form.save()
            messages.success(request, f"Reservación #{reserva.id} actualizada. Total: ${reserva.total} MXN.")
            return redirect('lista_reservaciones')
    else:
        form = ReservacionForm(instance=reservacion)

    return render(request, 'gestion/reservacion_form.html', {
        'form': form,
        'titulo': f'Modificar Reservación #{reservacion.id}'
    })


@login_required
def cancelar_reservacion(request, pk):
    reservacion = get_object_or_404(Reservacion, pk=pk)
    if request.method == 'POST':
        reservacion.estado = 'Cancelada'
        reservacion.save()
        messages.warning(request, f"La Reservación #{reservacion.id} ha sido cancelada.")
        return redirect('lista_reservaciones')

    return render(request, 'gestion/confirmar_eliminar.html', {
        'objeto': f"Reservación #{reservacion.id} (Hab. #{reservacion.habitacion.numero} - {reservacion.cliente})",
        'accion': 'Cancelar Reservación',
        'cancel_url': 'lista_reservaciones'
    })


@login_required
def consultar_disponibilidad(request):
    fecha_entrada = request.GET.get('fecha_entrada', '')
    fecha_salida = request.GET.get('fecha_salida', '')
    tipo = request.GET.get('tipo', '')
    habitaciones_libres = None
    error = None

    if fecha_entrada and fecha_salida:
        if fecha_salida <= fecha_entrada:
            error = "La fecha de salida debe ser mayor que la fecha de entrada."
        else:
            # Buscar IDs de habitaciones ocupadas en ese rango
            ocupadas_ids = Reservacion.objects.filter(
                estado__in=['Pendiente', 'Confirmada'],
                fecha_entrada__lt=fecha_salida,
                fecha_salida__gt=fecha_entrada
            ).values_list('habitacion_id', flat=True)

            habitaciones_libres = Habitacion.objects.filter(disponible=True).exclude(id__in=ocupadas_ids)
            if tipo:
                habitaciones_libres = habitaciones_libres.filter(tipo=tipo)

    context = {
        'fecha_entrada': fecha_entrada,
        'fecha_salida': fecha_salida,
        'tipo': tipo,
        'tipos': Habitacion.TIPOS_HABITACION,
        'habitaciones_libres': habitaciones_libres,
        'error': error,
    }
    return render(request, 'gestion/disponibilidad.html', context)


# ==========================================
# MÓDULO REPORTES Y ESTADÍSTICAS
# ==========================================
@login_required
def reportes(request):
    por_tipo = Habitacion.objects.values('tipo').annotate(
        total_habitaciones=Count('id', distinct=True),
        total_reservas=Count('reservaciones'),
        ingresos=Sum(
            'reservaciones__total',
            filter=Q(reservaciones__estado__in=['Confirmada', 'Completada'])
        )
    )
    por_estado = Reservacion.objects.values('estado').annotate(
        cantidad=Count('id'),
        monto=Sum('total')
    )
    context = {
        'por_tipo': por_tipo,
        'por_estado': por_estado,
    }
    return render(request, 'gestion/reportes.html', context)
