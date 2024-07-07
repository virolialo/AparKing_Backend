from django.db import models
from django.core.validators import MaxLengthValidator
from apps.authentication.models import CustomUser
from .enums import Status

class Report(models.Model):
    title = models.CharField(max_length=50, blank=False, null=False)
    category = models.CharField(max_length=25, blank=False, null=False)
    description = models.TextField(validators=[MaxLengthValidator(500)], default="Sin descripción")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDIENTE,
        blank=False,
        null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'status': self.status,
            'created_at': str(self.created_at),
        }