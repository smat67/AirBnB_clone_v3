#!/usr/bin/python3
"""This module defines views for state object"""
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.state import State


@app_views.route('/states',
                 methods=['GET', 'POST'], strict_slashes=False)
def states():
    """Retrieves the list of all State objects"""
    if request.method == 'GET':
        states = storage.all(State)
        result = []

        for state in states.values():
            result.append(state.to_dict())
        return jsonify(result)
    elif request.method == 'POST':
        if not request.json:
            abort(400, jsonify({"error": "Not a JSON"}))
        details = request.get_json()
        if "name" in details:
            name = details["name"]
            state = State(name=name)
            for k, v in details.items():
                setattr(state, k, v)
            state.save()
            return make_response(jsonify(state.to_dict()), 201)
        abort(400, jsonify({"error": "Missing name"}))


@app_views.route('states/<uuid:state_id>',
                 methods=['GET', 'DELETE', 'PUT'], strict_slashes=False)
def states_id(state_id):
    """Retrieves a State object by its id"""
    state = storage.get(State, state_id)
    if state is not None:
        if request.method == 'GET':
            return jsonify(state.to_dict())
        if request.method == 'DELETE':
            state.delete()
            storage.save()
            return make_response(jsonify({}), 200)
        if request.method == 'PUT':
            if not request.json:
                abort(400, jsonify({"error": "Not a JSON"}))
            details = request.get_json()
            forbidden = ["id", "created_at", "updated_at"]
            for k, v in details.items():
                if k not in forbidden:
                    setattr(state, k, v)
            state.save()
            return make_response(jsonify(state.to_dict()), 200)
    abort(404, jsonify({"error": "Not found"}))
