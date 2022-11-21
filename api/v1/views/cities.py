#!/usr/bin/python3
"""This module defines views for city object"""
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.city import City
from models.state import State


@app_views.route('/states/<state_id>/cities',
                 methods=['GET'], strict_slashes=False)
def cities(state_id):
    """Retrieves the list of all city objects"""
    state = storage.get(State, state_id)

    if not state:
        abort(404, jsonify({"error": "Not found"}))
    return jsonify([city.to_dict() for city in state.cities])


@app_views.route('/states/<state_id>/cities',
                 methods=['POST'], strict_slashes=False)
def cities_post(state_id):
    """Create a new city"""
    state = storage.get(State, state_id)
    if not state:
        abort(404, jsonify({"error": "Not found"}))
    if not request.json:
        abort(400, jsonify({"error": "Not a JSON"}))
    details = request.get_json()
    if "name" not in details:
        abort(400, jsonify({"error": "Missing name"}))
    name = details["name"]
    city = City(name=name, state_id=state_id)
    for k, v in details.items():
        setattr(city, k, v)
    storage.new(city)
    storage.save()
    return make_response(jsonify(city.to_dict()), 201)


@app_views.route('cities/<city_id>',
                 methods=['GET', 'DELETE', 'PUT'], strict_slashes=False)
def city_id(city_id):
    """Retrieves a city object by its id"""
    city = storage.get(City, city_id)
    if city is not None:
        if request.method == 'GET':
            return jsonify(city.to_dict())

        if request.method == 'DELETE':
            city.delete()
            storage.save()
            return make_response(jsonify({}), 200)

        if request.method == 'PUT':
            if not request.json:
                abort(400, jsonify({"error": "Not a JSON"}))
            details = request.get_json()
            forbidden = ["id", "created_at", "updated_at", "state_id"]
            for k, v in details.items():
                if k not in forbidden:
                    setattr(city, k, v)
            city.save()
            return make_response(jsonify(city.to_dict()), 200)
    abort(404, jsonify({"error": "Not found"}))
