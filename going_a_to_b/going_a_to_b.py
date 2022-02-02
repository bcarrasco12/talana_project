import math
import requests

host = 'http://localhost:8000'
api_get_service_area = 'api/adventure/service-area'
api_get_vehicle = 'api/adventure/vehicle'

# =======================================================================
# response is a list result of method
# It is a list of dictionary. Each item has a kilometer -> identification
# of service area and refueling -> quantity of fuel have to charge to go 
# to the next services area
# =======================================================================
response = []

def call_api(method: str, url: str):    
    router_method = {
        'GET': requests.get(url),
        'POST': '',
        'PUT': ''
    }
    
    return router_method.get(method.upper())

def find_rute(service_area_from: dict, service_area_until: dict, vehicle: dict):    
    if (
        not service_area_from.get("right_station") 
        and service_area_from.get('kilometer') != service_area_until.get('kilometer')
    ):
        raise Exception("it is not possible to reach point b")   

    # =======================================================================
    # Call api to get data of next node
    # =======================================================================
    kilometer_from_ = service_area_from.get("right_station")
    response_service_area_node = call_api('GET', 
                                          f'{host}/{api_get_service_area}/{kilometer_from_}/')
    service_area_node = None
    if response_service_area_node.status_code in [201, 200]:
        service_area_node = response_service_area_node.json()
    else:
        raise Exception("Error with services area from")  

    # =======================================================================
    # Validate if this node is the point B
    # =======================================================================
    if service_area_node.get("kilometer") == service_area_until.get("kilometer"):        
        response.append({
            "kilometer": service_area_node.get("kilometer"),
            "refueling": None
        })        
        return True

    # =======================================================================
    # Validate if it's possible go to the next node
    # =======================================================================
    kilometers_traveled = service_area_node.get("kilometer") - service_area_from.get('kilometer')
    total_fuel = vehicle.get("fuel_actually") * vehicle.get("fuel_efficiency")

    if kilometers_traveled > total_fuel:
        raise Exception("it is not possible to reach point b")

    # =======================================================================
    # Calculate quantity of fuel have to charge to go to the next services area
    # =======================================================================
    consumed_gasoline = math.ceil(kilometers_traveled / vehicle.get("fuel_efficiency"))

    fuel_actually = round(vehicle.get("fuel_actually") - consumed_gasoline)

    next_point = service_area_node.get("right_station")

    fuel_required = math.ceil(next_point / vehicle.get("fuel_efficiency"))

    if fuel_required > fuel_actually:
        refueling = fuel_required - fuel_actually

        if refueling > vehicle.get("fuel_tank_size"):
            raise Exception("it is not possible to reach point b")

        vehicle["fuel_actually"] = fuel_actually + refueling

    else:
        refueling = None
        vehicle["fuel_actually"] = fuel_actually

    response.append({
        "kilometer": service_area_node.get("kilometer"),
        "refueling": refueling
    })

    find_rute(service_area_node, service_area_until, vehicle)

    

def get_rute(kilometer_from_: int, kilometer_until_: int, number_plate: str):
    # =======================================================================
    # Validate if point A is equal to point B
    # =======================================================================
    if kilometer_from_ == kilometer_until_:
        return []  

    # =======================================================================
    # Call api to get data of point A
    # =======================================================================
    response_service_area_from = call_api('GET', 
                                          f'{host}/{api_get_service_area}/{kilometer_from_}/')
    service_area_from = None
    if response_service_area_from.status_code in [201, 200]:
        service_area_from = response_service_area_from.json()
    else:
        raise Exception("Error with services area from")  

    # =======================================================================
    # Call api to get data of point B
    # =======================================================================
    response_service_area_until = call_api("GET", 
                                           f'{host}/{api_get_service_area}/{kilometer_until_}/'
                                  )
    service_area_until = None
    if response_service_area_until.status_code in [201, 200]:
        service_area_until = response_service_area_until.json()
    else:
        raise Exception("Error with services area from")  

    if service_area_from.get("kilometer") > service_area_until.get("kilometer"):
        raise Exception("It is not possible to return") 

    # =======================================================================
    # Call api to get data of vehicle
    # =======================================================================
    response_vehicle = call_api("GET", f'{host}/{api_get_vehicle}/{number_plate}/')   
    vehicle = None 
    if response_vehicle.status_code in [201, 200]:
        vehicle = response_vehicle.json()
    else:
        raise Exception("Error with vehicle")

    vehicle["fuel_actually"] = vehicle.get("fuel_tank_size")

    # =======================================================================
    # Get route
    # =======================================================================    
    find_rute(service_area_from, service_area_until, vehicle)
    
    print(response)
    

get_rute(50,980,'AA-22-33')