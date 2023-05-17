# challenge NeuralWorks

## Tecnologías
- Base de datos: PostreSQL/PostGIS
- Backend: Flask
- Test de carga: Artillery
- Contenedor: Docker

### Bibliotecas de python
- Flask
- sqlalchemy
- flask_sqlalchemy
- geoalchemy2

## Configuración de base de datos
La base de datos que se utiliza es PostgreSQL con PostGIS para la manipulación de datos geoespaciales.

La imagen utilizada se obtiene de https://registry.hub.docker.com/r/postgis/postgis/

La base de datos contiene una tabla llamada "trips" la cual tiene las siguientes columnas
- region: text
- origin_coord: geom(point)
- destination_coord: geom(point)
- datetime: datetime
- datasource: text

La base de datos se indexa con el siguiente comando: 
``` sql
CREATE INDEX trips_idx ON trips USING GIST (origin_coord, destination_coord);   
```
para así crear un índice basado en los puntos geoespaciales de origen y destino.

## Query utilizada para obtener viajes semanales
``` sql
SELECT AVG(weekly_trips_count.count)
FROM (SELECT (COUNT(id)), DATE_PART('week', datetime)
FROM trips 
WHERE ST_Contains(ST_MakeEnvelope(minx,miny,maxx,maxy), origin_coord) AND ST_Contains(ST_MakeEnvelope(minx,miny,maxx,maxy), destination_coord) AND region  = <region>
GROUP BY DATE_PART('week', datetime)) as weekly_trips_count;   
```
La función ST_Contains indica si un punto se encuentra dentro de un polígono o no. ST_Contains(A,B) retorna TRUE si el punto B se encuentra dentro del polígono A. La función ST_MakeEnvelope(minx,miny,maxx,maxy) genera un polígono en función de las coordenadas ingresadas.


## Rutas

### /trips [POST]
Esta ruta permite agregar un nuevo viaje a la base de datos. Se recibe un json payload con los datos que se desean almacenar, de la forma:
``` javascript
    {
        region: string,
        origin_coord: string,
        destination_coord: string,
        datetime: string,
        datasource: string
    }
```

Un ejemplo es:
``` javascript
    {
        region: 'Prague',
        origin_coord: 'POINT (14.56861581242726 50.10620152153201)',
        destination_coord: 'POINT (14.31831785619946 49.999311030748)',
        datetime: '2018-05-03 05:24:26.000',
        datasource: 'baba_car'
    }
```

### /trips/<id> [GET]
Esta ruta permite obtener un viaje de la base de datos dado un ID.
  
### /trips/post_random_trip [GET]
Esta ruta publica un viaje aleatorio en la base de datos.
  
### /trips/weekly [GET]
Esta ruta obtiene el promedio semanal de la cantidad de viajes para un área definida por un bounding box y la región. Recibe un payload json para indicar las condiciones del bounding box y la región.

Un ejemplo de payload es:
``` javascript
  {
    "xmin": 14,
    "ymin": 50,
    "xmax": 16,
    "ymax": 51,
    "region": "Prague"
  }
```
 
  
