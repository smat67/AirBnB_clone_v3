#!/usr/bin/python3
"""This module defines views for Review object"""
from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.review import Review
from models.place import Place


@app_views.route('/places/<place_id>/reviews',
                 methods=['GET'], strict_slashes=False)
def review(place_id):
    """Retrieves the list of all reviews for a place objects"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404, jsonify({"error": "Not found"}))

    return jsonify([review.to_dict() for review in place.reviews])


@app_views.route('/places/<place_id>/reviews',
                 methods=['POST'], strict_slashes=False)
def review_post(place_id):
    """creates a new review object """
    place = storage.get(Place, place_id)
    if not place:
        abort(404, jsonify({"error": "Not found"}))
    details = request.get_json()
    if not details:
        abort(400, jsonify({"error": "Not a JSON"}))

    if "user_id" not in details:
        abort(400, jsonify({"error": "Missing user_id"}))

    user_id = details["user_id"]
    if not storage.get("User", user_id):
        abort(404, jsonify({"error": "Not found"}))
    if "text" not in details:
        abort(400, jsonify({"error": "Missing text"}))
    review = Review(**details)
    storage.new(review)
    storage.save()
    return make_response(jsonify(review.to_dict()), 201)


@app_views.route('/reviews/<review_id>', methods=['GET', 'DELETE', 'PUT'],
                 strict_slashes=False)
def handle_review(review_id):
    """Handles basic method of the reviews endpoint"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404, jsonify({"error": "Not found"}))

    # if request method is GET
    if request.method == 'GET':
        return jsonify(review.to_dict())

    # if request method is Delete, delete review
    if request.method == 'DELETE':
        review.delete()
        storage.save()
        return make_response(jsonify({}), 200)

    # if request method == PUT, update review
    if request.method == 'PUT':
        if not request.json():
            abort(400, jsonify({"error": "Not a JSON"}))
        details = request.get_json()
        for k, v in details.items():
            if k not in ['id', 'user_id', 'place_id',
                         'created_at', 'updated_at']:
                setattr(review, k, v)
        storage.save()
        return make_response(jsonify(review.to_dict()), 200)
