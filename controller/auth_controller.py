# Auth Controller

from flask import Blueprint, request, jsonify, make_response, session


auth = Blueprint("auth", __name__)

@auth.route("/test", methods=["GET"])
def root():
    return make_response(jsonify({"message": "Auth API is up and running."}), 200)
