from django.db import models
from datetime import date

# Create your models here.
class Prohibidos(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()

    def __str__(self):
        return f"{self.rut} - {self.nombre}"
    
    @property
    def esta_vigente(self):
        hoy = date.today()
        return self.fecha_inicio <= hoy <= self.fecha_termino

class Autoexcluidos(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=200, null=True)
    apellido_pat = models.CharField(max_length=100, null=True)
    apellido_mat = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    telefono = models.CharField(max_length=100, null=True)
    telefono_movil = models.CharField(max_length=100, null=True)
    ap_inscrito = models.CharField(max_length=100, null=True)
    ap_aceptado = models.CharField(max_length=100, null=True)
    nombre_ap = models.CharField(max_length=200, null=True)
    apellido_pat_ap = models.CharField(max_length=100, null=True)
    apellido_mat_ap = models.CharField(max_length=100, null=True)
    email_ap = models.CharField(max_length=100, null=True)
    telefono_ap = models.CharField(max_length=100, null=True)
    telefono_movil_ap = models.CharField(max_length=100, null=True)
    activo = models.CharField(max_length=100, null=True)
    fecha_ae = models.DateField(null=True)

    def __str__(self):
        return f"{self.rut} - {self.nombre} - {self.fecha_ae}"
    
class Sospechosos(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.rut} - {self.nombre}"

class Seguimientos(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.rut} - {self.nombre}"

class Peps(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.rut} - {self.nombre}"