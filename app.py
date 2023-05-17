from flask import Flask
from flask import jsonify
from flask import request
from flask import make_response
from flask_migrate import Migrate
from models import db, Trip
from sqlalchemy import create_engine, MetaData, text
from flask_sqlalchemy import SQLAlchemy
import random
import datetime

random.seed(10)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
migrate = Migrate(app, db)


@app.route('/trips', methods=['POST'])
def postTrip():
    '''
    En esta función se publica un viaje en la base de datos. Recibe un payload en formato JSON de la forma
    {
        region: string,
        origin_coord: string,
        destination_coord: string,
        datetime: string,
        datasource: string
    }
    '''
    req = request.get_json()
    trip = Trip(region=req.get('region'), origin_coord=req.get('origin_coord'), destination_coord=req.get(
        'destination_coord'), datetime=req.get('datetime'), datasource=req.get('datasource'))
    db.session.add(trip)
    db.session.commit()
    response = make_response("<h1>Success</h1>")
    response.status_code = 200
    return response


@app.route('/trips/post_random_trip', methods=['GET'])
def postRandomTrip():
    '''
    Esta función publica un viaje aleatorio en la base de datos.
    Se usa para testear el posteo de datos.
    '''
    regions = ['Prague', 'Hamburg', 'Turin']
    datasources = ['funny_car', 'baba_car', 'cheap_mobile',
                   'bad_diesel_vehicles', 'pt_search_app']
    datasource = random.choice(datasources)
    timestamp = datetime.datetime(2018, random.randint(1, 12), random.randint(
        1, 31), random.randint(1, 24), random.randint(1, 60), random.randint(1, 60))
    region = random.choice(regions)
    origin_coords_x = 0
    origin_coords_y = 0
    destination_coords_x = 0
    destination_coords_y = 0
    if region == 'Prague':
        origin_coords_x = random.uniform(14, 15)
        origin_coords_y = random.uniform(50, 51)
        destination_coords_x = random.uniform(14, 15)
        destination_coords_y = random.uniform(50, 51)
    elif region == 'Turin':
        origin_coords_x = random.uniform(7, 8)
        origin_coords_y = random.uniform(45, 46)
        destination_coords_x = random.uniform(7, 8)
        destination_coords_y = random.uniform(45, 46)
    else:
        origin_coords_x = random.uniform(9, 11)
        origin_coords_y = random.uniform(53, 54)
        destination_coords_x = random.uniform(9, 11)
        destination_coords_y = random.uniform(53, 54)

    origin_coord = 'POINT (' + str(origin_coords_x) + \
        ' ' + str(origin_coords_y) + ')'
    destination_coord = 'POINT (' + str(destination_coords_x) + \
        ' ' + str(destination_coords_y) + ')'
    trip = Trip(region=region, origin_coord=origin_coord,
                destination_coord=destination_coord, datetime=timestamp, datasource=datasource)
    db.session.add(trip)
    db.session.commit()
    response = make_response("<h1>Success</h1>")
    response.status_code = 200
    return response


@app.route('/trips/<id>', methods=['GET'])
def findTrip(id):
    '''
    Esta función permite encontrar un viaje según ID de la base de datos.
    '''
    trip = Trip.query.get(id)
    return jsonify(trip.serialize())


@app.route('/trips/weekly', methods=['GET'])
def getAvgTripsPerWeek():
    '''
    Esta función devuelve el promedio semanal de la cantidad de viajes para un 
    área definida por un bounding box y la región.
    '''
    req = request.get_json()
    xmin = req.get('xmin')
    ymin = req.get('ymin')
    xmax = req.get('xmax')
    ymax = req.get('ymax')
    region = req.get('region')
    params = {'xmin': xmin, 'ymin': ymin,
              'xmax': xmax, 'ymax': ymax, 'region': region}
    sql = text("SELECT AVG(weekly_trips_count.count) FROM (SELECT (COUNT(id)), DATE_PART('week', datetime) FROM trips  WHERE ST_Contains(ST_MakeEnvelope(:xmin,:ymin,:xmax,:ymax), origin_coord) and ST_Contains(ST_MakeEnvelope(:xmin,:ymin,:xmax,:ymax), destination_coord) and region  = :region GROUP BY DATE_PART('week', datetime)) as weekly_trips_count;")
    result = db.session.execute(sql, params)
    return jsonify(list(result)[0][0])


if __name__ == '__main__':
    app.run(debug=True)
