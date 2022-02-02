from rest_framework.serializers import CharField, IntegerField, Serializer

# from adventure import models  # No se está utilizando


class JourneySerializer(Serializer):
    name = CharField()
    passengers = IntegerField()     

