from rest_framework import serializers
from .models import Report
import re

class ReportSerializer(serializers.ModelSerializer):

    CATEGORY = [
        "bug", "reservas", "cesiones", "garajes", "vehiculos", "otro"]

    class Meta:
        model = Report
        fields = ('title', 'category', 'description', 'user', 'created_at', 'status')

    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("El título no puede estar vacío.")
        if len(value) > 50:
            raise serializers.ValidationError("El título no puede superar los 50 caracteres.")
        return value

    def validate_description(self, value):
        if not value:
            raise serializers.ValidationError("La descripción no puede estar vacía.")
        if len(value) > 500:
            raise serializers.ValidationError("La descripción no puede superar los 500 caracteres.")
        return value
    
    def validate_category(self, value):
        if value.lower() not in self.CATEGORY:
            raise serializers.ValidationError("El motivo ingresado no es válido.")
        return value
    
    def create(self, validated_data):
        report = Report.objects.create(
            title=validated_data["title"],
            category=validated_data["category"],
            description=validated_data["description"],
            user=validated_data["user"],
        )
        return report