from django import forms
from .models import Habitacion, Cliente, Reservacion


class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['numero', 'tipo', 'precio_noche', 'capacidad', 'disponible', 'imagen']
        widgets = {
            'numero': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. 101',
                'min': '1'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'precio_noche': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. 1500.00',
                'step': '0.01',
                'min': '1'
            }),
            'capacidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. 2',
                'min': '1',
                'max': '10'
            }),
            'disponible': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellidos', 'correo', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre(s)'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'cliente@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. 8112345678'
            }),
        }


class ReservacionForm(forms.ModelForm):
    class Meta:
        model = Reservacion
        fields = ['cliente', 'habitacion', 'fecha_entrada', 'fecha_salida', 'estado']
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'form-select'
            }),
            'habitacion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_entrada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'fecha_salida': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que al editar una reserva existente, las fechas carguen en el input HTML5
        self.fields['fecha_entrada'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_salida'].input_formats = ['%Y-%m-%d']
        # Al crear una nueva reserva, mostrar solo habitaciones marcadas como disponibles
        if not self.instance.pk:
            self.fields['habitacion'].queryset = Habitacion.objects.filter(disponible=True)