#!/usr/bin/python3
"""This module defines views for place object"""
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.place import Place
from models.user import User
from models.city import City
from models.state import State
from models.amenity import Amenity


@app_views.route('/cities/<city_id>/places',
                 methods=['GET', 'POST'], strict_slashes=False)
def places(city_id):
    """Retrieves the list of all place objects"""
    city = storage.get(City, city_id)
    if not city:
        abort(404, jsonify({"error": "Not found"}))

    if request.method == 'GET':
        return jsonify([place.to_dict() for place in city.places])

    elif request.method == 'POST':
        if not request.json:
            abort(400, jsonify({"error": "Not a JSON"}))
        details = request.get_json()
        if "user_id" not in details:
            abort(400, jsonify({"error": "Missing user_id"}))
        user_id = details["user_id"]
        user = storage.get(User, user_id)
        if "name" not in details:
            abort(400, jsonify({"error": "Missing name"}))
        place = Place(name=details["name"])
        setattr(place, 'city_id', city_id)
        setattr(place, 'user_id', user_id)
        storage.new(place)
        storage.save()
        return make_response(jsonify(place.to_dict()), 201)


@app_views.route('places/<place_id>',
                 methods=['GET', 'DELETE', 'PUT'], strict_slashes=False)
def place_id(place_id):
    """Retrieves a place object by its id"""
    place = storage.get(Place, place_id)
    if place is not None:
        if request.method == 'GET':
            return jsonify(place.to_dict())

        if request.method == 'DELETE':
            place.delete()
            storage.save()
            return make_response(jsonify({}), 200)

        if request.method == 'PUT':
            if not request.json:
                abort(400, jsonify({"error": "Not a JSON"}))
            details = request.get_json()
            forbidden = ["id", "user_id",
                         "city_id", "created_at",
                         "updated_at", "place_id"]
            for k, v in details.items():
                if k not in forbidden:
                    setattr(place, k, v)
            storage.save()
            return make_response(jsonify(place.to_dict()), 200)
    abort(404, jsonify({"error": "Not found"}))


@app_views.route('/places_search', methods=['POST'],
                 strict_slashes=False)
def places_search():
    """
    Retrieves all Place objects depending of
    the JSON in the body of the request
    """
    body_r = request.get_json()
    if body_r is None:
        abort(400, jsonify({"error": "Not a JSON"}))

    if not body_r or (
            not body_r.get('states') and
            not body_r.get('cities') and
            not body_r.get('amenities')
    ):
        places = storage.all(Place)
        return jsonify([place.to_dict() for place in places.values()])

    places = []

    if body_r.get('states'):
        states = [storage.get(State, id) for id in body_r.get('states')]

        for state in states:
            for city in state.cities:
                for place in city.places:
                    places.append(place)

    if body_r.get('cities'):
        cities = [storage.get(City, id) for id in body_r.get('cities')]

        for city in cities:
            for place in city.places:
                if place not in places:
                    places.append(place)

    if not places:
        places = storage.all(Place)
        places = [place for place in places.values()]

    if body_r.get('amenities'):
        ams = [storage.get(Amenity, id) for id in body_r.get('amenities')]
        i = 0
        limit = len(places)
        HBNB_API_HOST = getenv('HBNB_API_HOST')
        HBNB_API_PORT = getenv('HBNB_API_PORT')

        port = 5000 if not HBNB_API_PORT else HBNB_API_PORT
        first_url = "http://0.0.0.0:{}/api/v1/places/".format(port)
        while i < limit:
            place = places[i]
            url = first_url + '{}/amenities'
            req = url.format(place.id)
            response = requests.get(req)
            am_d = json.loads(response.text)
            amenities = [storage.get(Amenity, o['id']) for o in am_d]
            for amenity in ams:
                if amenity not in amenities:
                    places.pop(i)
                    i -= 1
                    limit -= 1
                    break
            i += 1
    return jsonify([place.to_dict() for place in places])
