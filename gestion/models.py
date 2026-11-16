from django.db import models
from django.core.exceptions import ValidationError


class Habitacion(models.Model):
    TIPOS_HABITACION = [
        ('Individual', 'Individual'),
        ('Doble', 'Doble'),
        ('Suite', 'Suite'),
        ('Presidencial', 'Presidencial'),
    ]

    numero = models.IntegerField(unique=True, verbose_name="Número de Habitación")  # Regla 3
    tipo = models.CharField(max_length=20, choices=TIPOS_HABITACION, verbose_name="Tipo")
    precio_noche = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por Noche")
    capacidad = models.IntegerField(verbose_name="Capacidad (personas)")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    imagen = models.ImageField(upload_to='habitaciones/', null=True, blank=True, verbose_name="Fotografía")

    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"
        ordering = ['numero']

    def __str__(self):
        return f"Habitación #{self.numero} - {self.tipo} (${self.precio_noche}/noche)"

    def tiene_reservas_activas(self):
        return self.reservaciones.filter(estado__in=['Pendiente', 'Confirmada']).exists()

    def delete(self, *args, **kwargs):
        # Regla 5: No se puede eliminar una habitación con reservaciones activas
        if self.tiene_reservas_activas():
            raise ValidationError("No se puede eliminar esta habitación porque tiene reservaciones activas.")
        super().delete(*args, **kwargs)


class Cliente(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    correo = models.EmailField(unique=True, verbose_name="Correo Electrónico")  # Regla 4
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombre} {self.apellidos} ({self.correo})"


class Reservacion(models.Model):
    ESTADOS_RESERVACION = [
        ('Pendiente', 'Pendiente'),
        ('Confirmada', 'Confirmada'),
        ('Completada', 'Completada'),
        ('Cancelada', 'Cancelada'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='reservaciones',
        verbose_name="Cliente"
    )
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.PROTECT,
        related_name='reservaciones',
        verbose_name="Habitación"
    )
    fecha_entrada = models.DateField(verbose_name="Fecha de Entrada")
    fecha_salida = models.DateField(verbose_name="Fecha de Salida")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total ($)")
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_RESERVACION,
        default='Confirmada',
        verbose_name="Estado"
    )

    class Meta:
        verbose_name = "Reservación"
        verbose_name_plural = "Reservaciones"
        ordering = ['-fecha_entrada']

    def __str__(self):
        return f"Reserva #{self.id} | Hab. {self.habitacion.numero} - {self.cliente.nombre} {self.cliente.apellidos}"

    def clean(self):
        super().clean()
        if self.fecha_entrada and self.fecha_salida:
            # Regla 2: La fecha de salida debe ser mayor que la fecha de entrada
            if self.fecha_salida <= self.fecha_entrada:
                raise ValidationError({
                    'fecha_salida': "La fecha de salida debe ser al menos un día posterior a la fecha de entrada."
                })

            # Regla 1: Una habitación no podrá reservarse dos veces en las mismas fechas
            if self.habitacion_id and self.estado != 'Cancelada':
                traslapes = Reservacion.objects.filter(
                    habitacion=self.habitacion,
                    estado__in=['Pendiente', 'Confirmada'],
                    fecha_entrada__lt=self.fecha_salida,
                    fecha_salida__gt=self.fecha_entrada
                )
                # Si estamos editando una reserva existente, excluirla de la validación
                if self.pk:
                    traslapes = traslapes.exclude(pk=self.pk)

                if traslapes.exists():
                    raise ValidationError(
                        f"La Habitación #{self.habitacion.numero} ya está reservada en ese rango de fechas."
                    )

    def save(self, *args, **kwargs):
        # Calcular automáticamente el total según las noches y el precio por noche
        if self.fecha_entrada and self.fecha_salida and self.habitacion_id:
            noches = (self.fecha_salida - self.fecha_entrada).days
            if noches > 0:
                self.total = noches * self.habitacion.precio_noche
        self.full_clean()
        super().save(*args, **kwargs)