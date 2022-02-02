from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView
from schema import And, Optional, Schema, Use

from adventure.models import ServiceArea, Vehicle, VehicleType
from adventure.notifiers import Notifier
from adventure.repositories import JourneyRepository
from adventure.serializers import JourneySerializer
from adventure.usecases import StartJourney


class VehicleAPIView(APIView):
    def get(self, request, number_plate) -> Response:    
        try:
            vehicle = Vehicle.objects.get(number_plate=number_plate)
            return Response(
                {
                    "id": vehicle.id,
                    "name": vehicle.name,
                    "passengers": vehicle.passengers,
                    "vehicle_type": vehicle.vehicle_type.name,
                    "fuel_efficiency": vehicle.fuel_efficiency,
                    "fuel_tank_size": vehicle.fuel_tank_size
                },
                status=201
            )
        except Vehicle.DoesNotExist:
            raise Exception("Vehicle not found")

    def post(self, request: Request) -> Response:        
        payload = request.data

        # Validation data
        schema = Schema(            
            {
                'name': And(str, len), 
                'vehicle_type': And(str, len),
                Optional('passengers'): And(Use(int), lambda n: n > 0),
                Optional('fuel_efficiency'): And(Use(int), lambda n: n > 0),
                Optional('fuel_tank_size'): And(Use(int), lambda n: n > 0),
                Optional('number_plate'): And(str, len)
            },
            ignore_extra_keys=True            
        )        

        copy_payload = payload.dict() if type(payload) != dict else payload

        if not schema.is_valid(copy_payload):
            raise Exception("Invalid data input")

        try:
            vehicle_type = VehicleType.objects.get(name=payload["vehicle_type"])
        except VehicleType.DoesNotExist:
            raise Exception("Vehicle type not found")

        vehicle = Vehicle.objects.create(
            name=payload["name"],
            passengers=payload["passengers"],
            vehicle_type=vehicle_type,
            fuel_efficiency=payload.get("fuel_efficiency", 0),
            fuel_tank_size=payload.get("fuel_tank_size", 0),
            number_plate=payload.get("number_plate", '')
        )
        return Response(
            {
                "id": vehicle.id,
                "name": vehicle.name,
                "passengers": vehicle.passengers,
                "vehicle_type": vehicle.vehicle_type.name,
            },
            status=201
        )

class ServiceAreaAPIView(APIView):
    def get(self, request, kilometer) -> Response:    
        try:
            service_area = ServiceArea.objects.get(kilometer=kilometer)
            return Response(
                {
                    "id": service_area.id,
                    "kilometer": service_area.kilometer,
                    "gas_price": service_area.gas_price,
                    "left_station": service_area.left_station.kilometer if service_area.left_station else None,
                    "right_station": service_area.right_station.kilometer if service_area.right_station else None
                },
                status=201
            )
        except ServiceArea.DoesNotExist:
            raise Exception("ServiceArea not found")

    def post(self, request: Request) -> Response:        
        payload = request.data

        # Validation data
        schema = Schema(            
            {
                'kilometer': And(Use(int), lambda n: n >= 0), 
                'gas_price': And(Use(int), lambda n: n > 0),
            },
            ignore_extra_keys=True           
        )                

        copy_payload = payload.dict() if type(payload) != dict else payload

        if not schema.is_valid(copy_payload):        
            raise Exception("Invalid data input")

        left_station = self.validate_station(payload.get("left_station"))

        if left_station == -1:
            raise Exception("Invalid left station")

        right_station = self.validate_station(payload.get("right_station"))

        if right_station == -1:
            raise Exception("Invalid right station")
                
        service_area = ServiceArea.objects.create(
            kilometer=payload["kilometer"],
            gas_price=payload["gas_price"],
            left_station=left_station,
            right_station=right_station
        )

        return Response(
            {
                "id": service_area.id,
                "kilometer": service_area.kilometer,
                "gas_price": service_area.gas_price,
                "left_station": service_area.left_station,
                "right_station": service_area.right_station
            },
            status=201
        )

    def validate_station(self, station: int):
        try:
            if station:
                return ServiceArea.objects.get(pk=station) 
            else:
                return None
        except ServiceArea.DoesNotExist:
            return -1


class StartJourneyAPIView(generics.CreateAPIView):
    serializer_class = JourneySerializer

    def perform_create(self, serializer) -> None:
        repo = self.get_repository()
        notifier = Notifier()
        usecase = StartJourney(repo, notifier).set_params(
            serializer.validated_data
        )
        try:
            usecase.execute()
        except StartJourney.CantStart as e:
            raise ValidationError({"detail": str(e)})

    def get_repository(self) -> JourneyRepository:
        return JourneyRepository()
        
