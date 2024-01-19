from flask import Blueprint, request, jsonify, make_response, session


user = Blueprint("user", __name__)

@user.route("/test", methods=["GET"])
def root():
    return make_response(jsonify({"message": "User API is up and running."}), 200)