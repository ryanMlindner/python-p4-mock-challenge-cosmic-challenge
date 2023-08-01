from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    serialize_rules = ('-missions.scientist', '-missions.planet')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    missions = db.relationship("Mission", cascade="all, delete-orphan", backref="planet")

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    serialize_rules = ('-missions.planet', '-missions.scientist')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    missions = db.relationship("Mission", cascade="all, delete-orphan", backref="scientist")

    @validates('name', 'field_of_study')
    def validate_scientist(self, key, entry):
        if key == 'name' :
            if entry == None or entry == '':
                raise ValueError("Scientist must have a name")
        if key == 'field_of_study':    
            if entry == None or entry == '':
                raise ValueError("field of study must exist")
        return entry


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    serialize_rules = ('-planet.missions', '-scientist.missions')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))

    @validates('name', 'scientist_id', 'planet_id')
    def validate_scientist(self, key, entry):
        if key == 'name' :
            if entry == None or entry == '':
                raise ValueError("Mission must have a name")
        if key == 'scientist_id':    
            if entry == None or entry == '':
                raise ValueError("Mission must have a scientist")
        if key == 'planet_id':    
            if entry == None or entry == '':
                raise ValueError("Mission must have a planet")
        return entry

