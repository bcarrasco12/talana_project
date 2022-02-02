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


class CreateVehicleAPIView(APIView):
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

        if not schema.is_valid(payload):
            return Response(
                {
                    "message": "Invalid data input"
                },
                status=400,
            )

        try:
            vehicle_type = VehicleType.objects.get(name=payload["vehicle_type"])
        except VehicleType.DoesNotExist:
            return Response(
                {
                    "message": "Vehicle type not found"
                },
                status=400,
            ) 

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
            status=201,
        )

class CreateServiceAreaAPIView(APIView):
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

        if not schema.is_valid(payload):
            return Response(
                {
                    "message": "Invalid data input"
                },
                status=400,
            )

        left_station = self.validate_station(payload.get("left_station"))

        if left_station == -1:
            return Response(
                {
                    "message": "Invalid left station"
                },
                status=400,
            )

        right_station = self.validate_station(payload.get("right_station"))

        if right_station == -1:
            return Response(
                {
                    "message": "Invalid right station"
                },
                status=400,
            )
        
        try:
            service_area = ServiceArea.objects.create(
                kilometer=payload["kilometer"],
                gas_price=payload["gas_price"],
                left_station=left_station,
                right_station=right_station
            )
        except Exception as error:
            return Response(
                {
                    "message": error
                },
                status=400,
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
