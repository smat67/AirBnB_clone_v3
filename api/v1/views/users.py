#!/usr/bin/python3
"""This module defines views for user object"""
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.user import User


@app_views.route('/users',
                 methods=['GET', 'POST'], strict_slashes=False)
def users():
    """Retrieves the list of all User objects"""
    if request.method == 'GET':
        users = storage.all(User)
        result = []

        for user in users.values():
            result.append(user.to_dict())
        return jsonify(result)
    elif request.method == 'POST':
        if not request.json:
            abort(400, jsonify({"error": "Not a JSON"}))
        details = request.get_json()
        if "email" not in details:
            abort(400, jsonify({"error": "Missing email"}))
        if "password" not in details:
            abort(400, jsonify({"error": "Missing password"}))
        user = User(email=details["email"], password=details["password"])
        for k, v in details.items():
            setattr(user, k, v)
        user.save()
        return make_response(jsonify(user.to_dict()), 201)


@app_views.route('users/<uuid:user_id>',
                 methods=['GET', 'DELETE', 'PUT'], strict_slashes=False)
def users_id(user_id):
    """Retrieves a User object by its id"""
    user = storage.get(User, user_id)
    if user is not None:
        if request.method == 'GET':
            return jsonify(user.to_dict())
        if request.method == 'DELETE':
            user.delete()
            storage.save()
            return make_response(jsonify({}), 200)
        if request.method == 'PUT':
            if not request.json:
                abort(400, jsonify({"error": "Not a JSON"}))
            details = request.get_json()
            forbidden = ["id", "email", "created_at", "updated_at"]
            for k, v in details.items():
                if k not in forbidden:
                    setattr(user, k, v)
            user.save()
            return make_response(jsonify(user.to_dict()), 200)
    abort(404, jsonify({"error": "Not found"}))
