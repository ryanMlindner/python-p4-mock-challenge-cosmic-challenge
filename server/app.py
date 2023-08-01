#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Index(Resource):
    def get(self):
        response_dict = {
            "index": "Cosmic. Cosmicness. Cosmicality."
        }
        response = make_response(response_dict, 200)
        return response

class Scientists(Resource):
    def get(self):
        scientists_dict = [scientist.to_dict(rules=('-missions',)) for scientist in Scientist.query.all()]

        response = make_response(scientists_dict, 200)
        return response

    def post(self):

        json = request.get_json()
        try:
            new_scientist = Scientist(
                name = json["name"],
                field_of_study = json["field_of_study"]
            )
            db.session.add(new_scientist)
            db.session.commit()
            scientist_dict = new_scientist.to_dict()

            response = make_response(
                scientist_dict,
                201
            )
            return response
        
        except ValueError:
            response = make_response(
                {"errors": ["validation errors"]},
                400
            )
            return response

class ScientistsByID(Resource):
    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist != None:
            response = make_response(scientist.to_dict(), 200)
        else:
            response = make_response({"error": "Scientist not found"}, 404)
        return response

    def patch(self, id):
        json = request.get_json()
        scientist = Scientist.query.filter(Scientist.id == id).first()
        try:
            if scientist != None:
                if json["name"] != None:
                    scientist.name = json["name"]
                if json["field_of_study"] != None:
                    scientist.field_of_study = json["field_of_study"]
                scientist_dict = scientist.to_dict(rules=('-missions',))
                response = make_response(scientist_dict, 202)

            else:
                response = make_response({"error": "Scientist not found"}, 404)
            return response
        except ValueError:
            response = make_response({"errors": ["validation errors"]},400)
            return response
    
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist != None:
            db.session.delete(scientist)
            db.session.commit()
            response = make_response({}, 204)
        else:
            response = make_response({"error": "Scientist not found"}, 404)
        return response
    
class Planets(Resource):
    def get(self):
        planets_dict = [planet.to_dict(rules=("-missions",)) for planet in Planet.query.all()]
        response = make_response(planets_dict, 200)
        return response

class Missions(Resource):
    def post(self):
        json = request.get_json()
        try:
            new_mission = Mission(
                name = json["name"],
                scientist_id = json["scientist_id"],
                planet_id = json["planet_id"],
            )
            db.session.add(new_mission)
            db.session.commit()
            response = make_response(new_mission.to_dict(), 201)
            return response
        except ValueError:
            response = make_response({"errors": ["validation errors"]},400)
            return response

api.add_resource(Index, '/')
api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistsByID, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
