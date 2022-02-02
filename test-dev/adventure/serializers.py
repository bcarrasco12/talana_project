from rest_framework.serializers import (CharField, DecimalField, IntegerField,
                                        Serializer)

# from adventure import models  # No se está utilizando


class JourneySerializer(Serializer):
    name = CharField()
    passengers = IntegerField()     
    number_plate = CharField()
    fuel_tank_size = DecimalField(max_digits=6, decimal_places=2)
