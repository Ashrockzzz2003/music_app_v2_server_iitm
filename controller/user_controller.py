from flask import Blueprint, jsonify, make_response

user = Blueprint("user", __name__)

@user.route("/test", methods=["GET"])
def root():
    return make_response(jsonify({"message": "User API is up and running."}), 200)