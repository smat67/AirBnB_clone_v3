#!/usr/bin/python3
"""This module defines views for Amenity object"""
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.amenity import Amenity


@app_views.route('/amenities',
                 methods=['GET', 'POST'], strict_slashes=False)
def amenities():
    """Retrieves the list of all Amenity objects"""
    if request.method == 'GET':
        amenities = storage.all(Amenity)
        result = []

        for amenity in amenities.values():
            result.append(amenity.to_dict())
        return jsonify(result)
    elif request.method == 'POST':
        if not request.json:
            abort(400, jsonify({"error": "Not a JSON"}))
        details = request.get_json()
        if "name" in details:
            name = details["name"]
            amenity = Amenity(name=name)
            for k, v in details.items():
                setattr(amenity, k, v)
            amenity.save()
            return make_response(jsonify(amenity.to_dict()), 201)
        abort(400, jsonify({"error": "Missing name"}))


@app_views.route('amenities/<uuid:amenity_id>',
                 methods=['GET', 'DELETE', 'PUT'], strict_slashes=False)
def amenities_id(amenity_id):
    """Retrieves a Amenity object by its id"""
    amenity = storage.get(Amenity, amenity_id)
    if amenity is not None:
        if request.method == 'GET':
            return jsonify(amenity.to_dict())
        if request.method == 'DELETE':
            amenity.delete()
            storage.save()
            return make_response(jsonify({}), 200)
        if request.method == 'PUT':
            if not request.json:
                abort(400, jsonify({"error": "Not a JSON"}))
            details = request.get_json()
            forbidden = ["id", "created_at", "updated_at"]
            for k, v in details.items():
                if k not in forbidden:
                    setattr(amenity, k, v)
            amenity.save()
            return make_response(jsonify(amenity.to_dict()), 200)
    abort(404, jsonify({"error": "Not found"}))
