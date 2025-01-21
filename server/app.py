#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
from werkzeug.exceptions import NotFound
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

# below, we monkey-patch flask-restful's Api class to overwrite it's error_router with Flask's native error handler so that we can use the custom errorhandler we've registered on app
Api.error_router = lambda self, handler, e: handler(e)
api = Api(app)

@app.route('/')
def home():
    return ''


@app.errorhandler(NotFound)
def handle_not_found(error):
	return make_response(
        {"error":"Scientist not found"},
		404
    )
app.register_error_handler(404, handle_not_found)


class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict(only=('id','name','field_of_study')) for scientist in Scientist.query.all()]
        return make_response(scientists, 200)
    
    def post(self):
        data = request.get_json()
        try:
            model = Scientist(
                name=data['name'],
                field_of_study=data['field_of_study']
            )
            db.session.add(model)
            db.session.commit()
            return make_response(model.to_dict(), 201)
        except Exception as e:
            return make_response({"errors": '["validation errors"]'}, 422)
            
class ScientistByID(Resource):
    @classmethod
    def find_model_by_id(cls, id):
        model = Scientist.query.get_or_404(id)
        return model
            
    def get(self, id):
        model = self.__class__.find_model_by_id(id)
        return model.to_dict(), 200
    
    def patch(self, id):
        data = request.get_json()
        model = self.__class__.find_model_by_id(id)
        try:
            for attr,value in data.items():
                setattr(model, attr, value)
            #db.session.add(model)
            db.session.commit()
            return make_response(model.to_dict(only=('id','name','field_of_study','missions')), 202)
        except Exception as e:
            return make_response({"errors": '["validation errors"]'}, 422)

    def delete(self, id):
        model = self.__class__.find_model_by_id(id)
        db.session.delete(model)
        db.session.commit()
        return make_response("", 204)

api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistByID, '/scientists/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
