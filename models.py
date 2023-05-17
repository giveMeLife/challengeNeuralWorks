from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from dataclasses import dataclass
from geoalchemy2.shape import to_shape   
from sqlalchemy import inspect

 
db = SQLAlchemy()

@dataclass
class Trip(db.Model):
    __tablename__ = 'trips'
 
    id = db.Column(db.Integer, primary_key = True)
    region = db.Column(db.String())
    origin_coord = db.Column(Geometry("POINT"))
    destination_coord = db.Column(Geometry("POINT"))
    datetime = db.Column(db.DateTime())
    datasource = db.Column(db.String())
 
    def __init__(self,region,origin_coord,destination_coord,datetime,datasource):
        self.region = region
        self.origin_coord = origin_coord
        self.destination_coord = destination_coord
        self.datetime = datetime
        self.datasource = datasource
        
    #Se serializa el modelo para poder retornarlo como JSON.
    #La función to_shape permite transformar el elemento GEOM de POSTGIS a un punto en python.
    def serialize(self):
        return {"id": self.id,
                "region": self.region,
                "origin_coord": str(to_shape(self.origin_coord)),
                "destination_coord": str(to_shape(self.destination_coord)),
                "datetime": str(self.datetime),
                "datasource": self.datasource}
        
    def __repr__(self):
        return f"<Trip {self.id}>"