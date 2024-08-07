import datetime
from django.contrib.gis.geos import Point
from rest_framework import serializers
from apps.parking.models import Parking, City
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from apps.parking.enums import ParkingType

class ParkingSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    cesion_parking = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S', required=False, allow_null=True)
    
    def validate_cesion_parking(self, value):
        """
        Valida que la fecha de cesion_parking no sea una fecha pasada
        y que el año sea el actual.
        """
        if value:
            now = datetime.now()
            if value < now:
                raise serializers.ValidationError("La fecha de cesión no puede ser en el pasado.")
            elif value.year != now.year:
                raise serializers.ValidationError("La fecha de cesión debe ser del año actual.")
        return value

    class Meta:
        model = Parking
        fields = '__all__'
        extra_kwargs = {
            'location': {'required': False},
            'notified_by': {'read_only': True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.location:
            representation['location'] = {
                'latitude': instance.location.y,
                'longitude': instance.location.x
            }
        return representation
    
    def validate(self, attrs):
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')

        if latitude is not None and longitude is not None:
            location = Point(longitude, latitude, srid=4326)
            exist = Parking.objects.annotate(distance=Distance('location', location)).filter(
                location__distance_lte=(location, D(m=10)),
                parking_type=ParkingType.FREE,
                is_transfer=False
            ).exists()

            if exist:
                raise serializers.ValidationError({'location': 'There is already a parking near you'})

        return super().validate(attrs)

    def create(self, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)

        if latitude is not None and longitude is not None:
            validated_data['location'] = Point(longitude, latitude, srid=4326)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)

        if latitude is not None and longitude is not None:
            instance.location = Point(longitude, latitude, srid=4326)

        instance.save()
        return super().update(instance, validated_data)
    
class CitySerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    class Meta:
        model = City
        fields = '__all__'
        read_only_fields = ['id'] 
        extra_kwargs = {
            'location': {'required': False},
        }

    def validate_location(self, value):
        """
        Valida el campo 'location' para asegurarse de que sea una instancia de GEOS Point.
        """
        if not value:
            raise serializers.ValidationError("La ubicación no puede estar vacía")
        if not isinstance(value, Point):
            raise serializers.ValidationError("La ubicación debe ser un punto GEOS válido")
        return value
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.location:
            representation['location'] = {
                'latitude': instance.location.y,
                'longitude': instance.location.x
            }
        return representation
    
    def create(self, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)

        if latitude is not None and longitude is not None:
            validated_data['location'] = Point(longitude, latitude, srid=4326)

        return super().create(validated_data)
    
    def get_distance(self, obj):
        distance_in_km = obj.distance.km  # Convierte la distancia a kilómetros
        return f"{distance_in_km:.2f} km"