from apps.garagement.models import Address, Availability, Garage, Image
from rest_framework import serializers
from . import validations


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"

    def validate(self, attrs):
        return validations.validate_address_data(attrs)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"

    def validate(self, attrs):
        return validations.validate_image_data(attrs)


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = "__all__"

    def validate(self, attrs):
        return validations.validate_availability_data(attrs)


class GarageSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Garage
        fields = "__all__"

    def validate(self, attrs):
        return validations.validate_garage_data(attrs)

    def create(self, validated_data):
        address_data = validated_data.pop("address")
        address = Address.objects.create(**address_data)
        image_data = validated_data.pop("image")

        image_file = image_data.pop("image", None)
        if image_file is not None:
            Image.objects.create(garage=garage, image=image_file, **image_data)
            garage = Garage.objects.create(
                address=address, image=image_file**validated_data
            )
        return garage

    # def update(self, instance, validated_data):
    #     address_data = validated_data.pop('address', None)
    #     if validated_data:
    #         for attr, value in validated_data.items():
    #             setattr(instance, attr, value)
    #         instance.save()

    #     if address_data:
    #         address = instance.address
    #         for attr, value in address_data.items():
    #             setattr(address, attr, value)
    #         address.save()

    #     return instance
