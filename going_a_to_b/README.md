# Going A to B

En este directorio, vas a encontrar un script de Python **going_a_to_b.py**, el cual permite obtener la ruta de un punto A a un punto B cualquiera, siempre y cuando B > A (ya que las instrucciones indican que no es posible devolverse: "Un viaje puede comenzar y terminar en cualquier punto de descanso, sin devolverse.").
Entregará como respuesta una lista de diccionarios que contine el área de servicio a visitar (identificada por la key kilometer, indicando el kilometraje del área de servicio), así como la cantidad de combustible a cargar (en litros), para poder llegar al siguiente punto.

## Consideraciones:
- El script ejecuta el método **get_rute**, el cual recibe como parámetros el punto A, punto B y la patente del vehículo a usar en el recorrido. Ej: (0,50,'AA-22-33')
- El punto A y B, están identificados por el kilómetro en el cual se encuentran
- Se incorporaron 2 apis en el proyecto Safari app "Adventure" para hacer posible la realización de este script
- Para su ejecución, puedes hacer uso de **docker-compose up**, pero debes tomar en cuenta que el proyecto Safari app "Adventure" ya debe estar ejecutandose para poder consultar las apis necesarias
