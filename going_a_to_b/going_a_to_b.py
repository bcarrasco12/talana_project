import requests

host = 'http://localhost:8000'
api_get_service_area = 'api/adventure/service-area'
api_get_vehicle = 'api/adventure/vehicle'

def call_api(method: str, url: str):
    print(url)
    router_method = {
        'GET': requests.get(url),
        'POST': '',
        'PUT': ''
    }
    
    return router_method.get(method.upper())

def find_rute(service_area_from: dict, service_area_until: dict, vehicle: dict, response: list):
    if (
        not service_area_from.get("right_station") 
        and service_area_from.get('kilometer') != service_area_until.get('kilometer')
    ):
        raise Exception("it is not possible to reach point b")   

    
    

def get_rute(kilometer_from_: int, kilometer_until_: int, number_plate: str):
    # =======================================================================
    # Validate if point A is equal to point B
    # =======================================================================
    if kilometer_from_ == kilometer_until_:
        return []  

    # =======================================================================
    # Call api to get data of point A
    # =======================================================================
    response_service_area_from = call_api('GET', f'{host}/{api_get_service_area}/{kilometer_from_}/')
    service_area_from = None
    if response_service_area_from.status_code in [201, 200]:
        service_area_from = response_service_area_from.json()
    else:
        raise Exception("Error with services area from")  

    # =======================================================================
    # Call api to get data of point B
    # =======================================================================
    response_service_area_until = call_api('GET', f'{host}/{api_get_service_area}/{kilometer_until_}/')
    service_area_until = None
    if response_service_area_until.status_code in [201, 200]:
        service_area_until = response_service_area_until.json()
    else:
        raise Exception("Error with services area from")  

    if service_area_from.get('kilometer') > service_area_until.get('kilometer'):
        raise Exception("It is not possible to return") 

    # =======================================================================
    # Call api to get data of vehicle
    # =======================================================================
    response_vehicle = call_api('GET', f'{host}/{api_get_vehicle}/{number_plate}/')   
    vehicle = None 
    if response_vehicle.status_code in [201, 200]:
        vehicle = response_vehicle.json()
    else:
        raise Exception("Error with vehicle")

    # =======================================================================
    # Get route
    # =======================================================================
    response = find_rute(service_area_from, service_area_until, vehicle, [])
    
    print(response)
    

get_rute(0,25,'AA-22-33')