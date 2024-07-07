from django.db import models

class Status(models.TextChoices):
    PENDIENTE = 'Pendiente', 'Pendiente'
    RESUELTO = 'Resuelto', 'Resuelto'
    CANCELADO = 'Cancelado', 'Cancelado'